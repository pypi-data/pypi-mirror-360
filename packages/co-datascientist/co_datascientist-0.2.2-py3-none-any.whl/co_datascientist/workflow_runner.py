import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import asyncio
from pathlib import Path
import httpx
from datetime import datetime

from .models import Workflow, SystemInfo, CodeResult
from . import co_datascientist_api
from .kpi_extractor import extract_kpi_from_stdout, create_kpi_folder_name, should_enable_kpi_naming
from .settings import settings

OUTPUT_FOLDER = "co_datascientist_output"
CHECKPOINTS_FOLDER = "co_datascientist_checkpoints"


def print_workflow_info(message: str):
    """Print workflow info with consistent formatting"""
    print(f"   {message}")


def print_workflow_step(message: str):
    """Print workflow step with consistent formatting"""
    print(f"   🔄 {message}")


def print_workflow_success(message: str):
    """Print workflow success with consistent formatting"""
    print(f"   ✅ {message}")


def print_workflow_error(message: str):
    """Print workflow error with consistent formatting"""
    print(f"   ❌ {message}")


class BestTracker:
    """Tracks the best result found so far"""
    
    def __init__(self, checkpoint_interval: int = 10):
        self.best_kpi: float | None = None
        self.best_code: str | None = None
        self.best_name: str | None = None
        self.best_result: CodeResult | None = None
        self.best_iteration: int = 0
        self.current_iteration: int = 0
        self.checkpoint_interval = checkpoint_interval
        self.last_checkpoint: int = 0
        self.checkpoint_count: int = 0
        
    def update(self, kpi: float | None, code: str, name: str, result: CodeResult) -> bool:
        """
        Update tracker with new result. Returns True if this is a new best.
        """
        self.current_iteration += 1
        
        # If no KPI extracted, skip this result
        if kpi is None:
            return False
            
        # If we have no best yet, or this is better
        if self.best_kpi is None or kpi > self.best_kpi:
            self.best_kpi = kpi
            self.best_code = code
            self.best_name = name
            self.best_result = result
            self.best_iteration = self.current_iteration
            return True
            
        return False
    
    def should_checkpoint(self) -> bool:
        """Check if we should save a checkpoint"""
        # Check if the next checkpoint is due within the current iteration count
        return self.current_iteration >= self.last_checkpoint + self.checkpoint_interval
    
    def mark_checkpoint(self):
        """Mark that we've saved a checkpoint"""
        self.last_checkpoint = self.current_iteration
    
    def get_progress_message(self) -> str:
        """Get current progress message"""
        if self.best_kpi is not None:
            return f"Best KPI: {self.best_kpi} (iteration {self.best_iteration}/{self.current_iteration})"
        else:
            return f"Iteration {self.current_iteration} (no KPI found yet)"


class _WorkflowRunner:
    def __init__(self):
        self.workflow: Workflow | None = None
        self.start_timestamp = 0
        self.should_stop_workflow = False
        self.debug_mode = True

    async def run_workflow(self, code: str, python_path: str, project_absolute_path: str, spinner=None, best_only: bool = False, checkpoint_interval: int = 10, batch_size: int = 1, max_concurrent: int = None, debug: bool = True):
        """Run a complete code evolution workflow"""
        self.should_stop_workflow = False
        
        # Set debug mode for the class instance
        self.debug_mode = debug
        
        # Default max_concurrent to batch_size (but capped at reasonable limit)
        if max_concurrent is None:
            max_concurrent = min(batch_size, 4)  # Cap at 4 to prevent resource exhaustion
        
        try:
            if spinner:
                spinner.text = "Initializing workflow..."
            self.start_timestamp = time.time()
            self.should_stop_workflow = False
            self.workflow = Workflow(status_text="Workflow started", user_id="")

            system_info = get_system_info(python_path)
            logging.info(f"user system info: {system_info}")
            
            if spinner:
                spinner.text = "Starting workflow..."
            response = await co_datascientist_api.start_workflow(code, system_info)
            self.workflow = response.workflow
            if spinner:
                spinner.stop()  # stop spinner without emoji
            print("Workflow started successfully")
            print()

            # Initialize best tracker if best_only mode is enabled
            best_tracker = None
            continuous_spinner_active = False
            if best_only:
                best_tracker = BestTracker(checkpoint_interval)

            # Always run in simple sequential mode (batch support removed)
            # For minimal mode, ensure we have a best_tracker
            if not self.debug_mode and best_tracker is None:
                best_tracker = BestTracker(checkpoint_interval)

            await self._run_sequential_mode(response, python_path, project_absolute_path,
                                            best_tracker, spinner, best_only)

            if self.should_stop_workflow:
                await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                print_workflow_info("Workflow stopped by user.")
                if spinner:
                    spinner.text = "Workflow stopped"
            else:
                # Check if workflow finished due to baseline failure or successful completion
                if (hasattr(self.workflow, 'baseline_code') and 
                    self.workflow.baseline_code.result is not None and 
                    self.workflow.baseline_code.result.return_code != 0):
                    print_workflow_error("Workflow terminated due to baseline code failure!")
                    print("   📄 Review the error details above and fix your script.")
                    if spinner:
                        spinner.text = "Workflow failed"
                else:
                    print_workflow_success("Workflow completed successfully!")
                    if best_only and best_tracker and best_tracker.best_kpi is not None:
                        print(f"   🏆 Final Best Result: KPI = {best_tracker.best_kpi} (iteration {best_tracker.best_iteration})")
                    if spinner:
                        spinner.text = "Workflow completed"
        
        except Exception as e:
            if spinner:
                spinner.stop()

            err_msg = str(e)
            # Detect user-facing validation errors coming from backend (prefixed with ❌)
            if err_msg.startswith("❌") and not self.debug_mode:
                # Show concise guidance without stack trace
                print_workflow_error(err_msg)
                return  # Do not re-raise, end gracefully

            # Otherwise, show generic workflow error and re-raise for full trace
            print_workflow_error(f"Workflow error: {err_msg}")
            raise

    async def _run_sequential_mode(self, response, python_path: str, 
                                  project_absolute_path: str, best_tracker: BestTracker = None,
                                  spinner=None, best_only: bool = False):
        """Run workflow in sequential mode (original behavior)"""
        
        continuous_spinner_active = False
        
        while not self.workflow.finished and response.code_to_run is not None and not self.should_stop_workflow:
            # Determine which mode we're in
            minimal_mode = not self.debug_mode and best_tracker is not None
            
            # Handle spinner differently based on mode
            if (best_only and best_tracker) or minimal_mode:
                # In best-only or minimal mode, start continuous spinner on first iteration
                if not continuous_spinner_active and spinner:
                    spinner.text = "Glowing up ✨" if minimal_mode else "Glowing Up ✨"
                    spinner.start()
                    continuous_spinner_active = True
            else:
                # Standard mode: stop spinner during code execution for clean output
                if spinner:
                    spinner.stop()
                print()  # Clean break instead of evaluating message
            
            result = _run_python_code(response.code_to_run.code, python_path)

            # Handle results based on mode
            if minimal_mode:
                show_result = await self._handle_minimal_mode_result(
                    result, response, project_absolute_path, best_tracker, spinner
                )
                # Only add spacing if we showed something
                if show_result:
                    print()
                    # Restart continuous spinner
                    if spinner:
                        spinner.text = "Glowing up ✨"
                        spinner.start()
                        continuous_spinner_active = True
            elif best_only and best_tracker:
                show_result = await self._handle_best_only_result(
                    result, response, project_absolute_path, best_tracker, spinner
                )
                # Only add spacing if we showed something
                if show_result:
                    print()
                    # Restart continuous spinner
                    if spinner:
                        spinner.text = "Glowing Up ✨"
                        spinner.start()
                        continuous_spinner_active = True
            else:
                await self._handle_standard_result(result, response, best_tracker)
                # Extra space before the next spinner line
                print()
                # Restart spinner while waiting for next idea
                if spinner:
                    spinner.text = "Generating new idea..."
                    spinner.start()

            # Prepare objects for backend
            kpi_value = extract_kpi_from_stdout(result.stdout)
            result.kpi = kpi_value
            code_version = response.code_to_run
            code_version.result = result

            response = await co_datascientist_api.finished_running_code(
                self.workflow.workflow_id,
                code_version,
                result,
                kpi_value,
            )
            self.workflow = response.workflow
            
            # Only add spacing in standard mode
            if not ((best_only and best_tracker) or minimal_mode):
                print()

    async def _handle_standard_result(self, result: CodeResult, response, best_tracker: BestTracker = None):
        """Handle result in standard mode (original behavior)"""
        # Check if code execution failed and provide clear feedback
        if result.return_code != 0:
            # Code failed - show error details
            print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
            if result.stderr:
                print("   📄 Error details:")
                # Print each line of stderr with proper indentation
                for line in result.stderr.strip().split('\n'):
                    print(f"      {line}")
            
            # For baseline failures, give specific guidance
            if response.code_to_run.name == "baseline":
                print("   💡 The baseline code failed to run. This will stop the workflow.")
                print("   💡 Check the error above and fix your script before running again.")
                if "ModuleNotFoundError" in (result.stderr or ""):
                    print("   💡 Missing dependencies? Try: pip install <missing-package>")
        else:
            # Code succeeded - show success message
            kpi_value = extract_kpi_from_stdout(result.stdout)
            if kpi_value is not None:
                print_workflow_success(f"Completed '{response.code_to_run.name}' | KPI = {kpi_value}")
            else:
                print_workflow_success(f"Completed '{response.code_to_run.name}'")

            # Update tracker with the new best result if we have one
            if best_tracker:
                is_new_best = best_tracker.update(kpi_value, response.code_to_run.code, response.code_to_run.name, result)
                if is_new_best:
                    print_workflow_success(f"🚀 New best KPI: {best_tracker.best_kpi} ({response.code_to_run.name})")

    async def _handle_best_only_result(self, result: CodeResult, response, project_absolute_path: str, best_tracker: BestTracker, spinner=None):
        """Handle result in best-only mode. Returns True if something was displayed."""
        showed_output = False
        
        if result.return_code != 0:
            # Code failed - only show baseline failures (critical setup issues)
            if response.code_to_run.name == "baseline":
                if spinner:
                    spinner.stop()
                print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
                if result.stderr:
                    print("   📄 Error details:")
                    for line in result.stderr.strip().split('\n'):
                        print(f"      {line}")
                showed_output = True
            else:
                # For evolve iterations, fail silently - just increment counter
                best_tracker.current_iteration += 1
        else:
            # Code succeeded - check if it's a new best
            kpi_value = extract_kpi_from_stdout(result.stdout)
            
            # Update tracker and check if this is a new best
            is_new_best = best_tracker.update(kpi_value, response.code_to_run.code, response.code_to_run.name, result)
            
            if is_new_best:
                if spinner:
                    spinner.stop()
                print_workflow_success(f"🚀 New best KPI: {best_tracker.best_kpi} ({response.code_to_run.name})")
                print(f"   📊 {best_tracker.get_progress_message()}")
                
                # Save the best result immediately
                await self._save_best_checkpoint(best_tracker, project_absolute_path)
                showed_output = True
            
            # Check if we should save a regular checkpoint
            elif best_tracker.should_checkpoint():
                if spinner:
                    spinner.stop()
                print(f"   📊 {best_tracker.get_progress_message()}")
                await self._save_best_checkpoint(best_tracker, project_absolute_path)
                showed_output = True
        
        return showed_output

    async def _handle_minimal_mode_result(self, result: CodeResult, response, project_absolute_path: str, best_tracker: BestTracker, spinner=None):
        """Handle result in minimal mode. Only shows rocket emoji for new best KPIs."""
        showed_output = False
        
        if result.return_code != 0:
            # Code failed - only show baseline failures (critical setup issues)
            if response.code_to_run.name == "baseline":
                if spinner:
                    spinner.stop()
                print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
                if result.stderr:
                    print("   📄 Error details:")
                    for line in result.stderr.strip().split('\n'):
                        print(f"      {line}")
                showed_output = True
            else:
                # For evolve iterations, fail silently - just increment counter
                best_tracker.current_iteration += 1
        else:
            # Code succeeded - check if it's a new best
            kpi_value = extract_kpi_from_stdout(result.stdout)
            
            # Update tracker and check if this is a new best
            is_new_best = best_tracker.update(kpi_value, response.code_to_run.code, response.code_to_run.name, result)
            
            if is_new_best:
                if spinner:
                    spinner.stop()
                # Simple rocket emoji output
                print(f"🚀 KPI: {best_tracker.best_kpi}")
                
                # Save the best result immediately
                await self._save_best_checkpoint(best_tracker, project_absolute_path)
                showed_output = True
        
        return showed_output

    async def _handle_batch_standard_results(self, results: list, batch: list):
        """Handle batch results in standard mode"""
        success_count = 0
        failure_count = 0
        
        print(f"🔍 [DEBUG] Processing {len(results)} batch results...")
        
        for i, (code_version_id, result) in enumerate(results):
            # Find the program name
            program_name = f"program_{i+1}"
            for code_version in batch:
                if code_version.code_version_id == code_version_id:
                    program_name = code_version.name or f"program_{i+1}"
                    break
            
            print(f"🐛 [DEBUG] Result {i+1}: {code_version_id[:12]}... -> {program_name}")
            
            if isinstance(result, Exception):
                print_workflow_error(f"Program {i+1}/{len(batch)} ({program_name}) crashed: {result}")
                print(f"   🐛 Exception type: {type(result).__name__}")
                failure_count += 1
            elif result.return_code != 0:
                print_workflow_error(f"Program {i+1}/{len(batch)} ({program_name}) failed with exit code {result.return_code}")
                if result.stderr:
                    print(f"   📄 Error snippet: {result.stderr[:100]}...")
                    print(f"   🔍 Full error saved in batch_debug_output/ files")
                failure_count += 1
            else:
                kpi_value = extract_kpi_from_stdout(result.stdout)
                if kpi_value is not None:
                    print_workflow_success(f"Program {i+1}/{len(batch)} ({program_name}) completed | KPI = {kpi_value}")
                else:
                    print_workflow_success(f"Program {i+1}/{len(batch)} ({program_name}) completed")
                success_count += 1
        
        print(f"📊 Batch Results: {success_count} succeeded, {failure_count} failed")
        if failure_count > 0:
            print(f"🔍 Check batch_debug_output/ for failed program code and detailed error messages")

    async def _handle_batch_best_only_results(self, results: list, batch: list, 
                                            project_absolute_path: str, best_tracker: BestTracker,
                                            spinner=None) -> bool:
        """Handle batch results in best-only mode. Returns True if something was displayed."""
        found_new_best = False
        for i, res_tuple in enumerate(results):
            if isinstance(res_tuple, tuple) and len(res_tuple) == 2:
                code_version_id, result = res_tuple
                program = next((p for p in batch if p.code_version_id == code_version_id), None)
                if program:
                    kpi = extract_kpi_from_stdout(result.stdout)
                    is_new_best = best_tracker.update(kpi, program.code, program.name, result)
                    if is_new_best:
                        found_new_best = True
                        print_workflow_success(f"🚀 New best KPI: {best_tracker.best_kpi} ({program.name})")
                else:
                    print_workflow_error(f"Could not find program for result {i}")
            elif isinstance(res_tuple, Exception):
                # Handle exceptions if needed
                pass

        # After the batch, check for checkpoint
        if best_tracker.should_checkpoint():
            await self._save_best_checkpoint(best_tracker, project_absolute_path)
            best_tracker.mark_checkpoint()
            
        if spinner:
            spinner.text = best_tracker.get_progress_message()
            
        return found_new_best

    async def _save_best_checkpoint(self, best_tracker: BestTracker, project_absolute_path: str):
        """Save the best program so far to a checkpoint folder"""
        
        if not best_tracker.best_code or not best_tracker.best_result:
            return

        # Create the main checkpoints folder if it doesn't exist
        checkpoints_base_dir = os.path.join(project_absolute_path, CHECKPOINTS_FOLDER)
        os.makedirs(checkpoints_base_dir, exist_ok=True)
        
        # Create the specific checkpoint subfolder
        checkpoint_subfolder_name = f"checkpoint_{best_tracker.checkpoint_count}"
        checkpoint_dir = os.path.join(checkpoints_base_dir, checkpoint_subfolder_name)
        os.makedirs(checkpoint_dir, exist_ok=True)

        # Name for files inside checkpoint folder
        base_name = f"best_iter_{best_tracker.best_iteration}_{_make_filesystem_safe(best_tracker.best_name)}"
        code_path = os.path.join(checkpoint_dir, f"{base_name}.py")
        result_path = os.path.join(checkpoint_dir, f"{base_name}_result.json")

        try:
            with open(code_path, "w", encoding='utf-8') as f:
                f.write(best_tracker.best_code)
            
            with open(result_path, "w", encoding='utf-8') as f:
                # Assuming best_result is a Pydantic model
                json.dump(best_tracker.best_result.model_dump(), f, indent=4)
                
            print_workflow_info(f"💾 Checkpoint {best_tracker.checkpoint_count} saved to {checkpoint_subfolder_name}")
            
            # Increment for the next checkpoint
            best_tracker.checkpoint_count += 1
            
        except IOError as e:
            print_workflow_error(f"Failed to save checkpoint files: {e}")
        except Exception as e:
            print_workflow_error(f"An unexpected error occurred during checkpoint save: {e}")

    async def _save_batch_to_generation_folder(self, batch: list, results: list, project_absolute_path: str):
        """Saves all programs from a batch into a generation-specific folder."""
        
        output_folder = Path(project_absolute_path) / OUTPUT_FOLDER
        output_folder.mkdir(parents=True, exist_ok=True)
        
        for i, code_version in enumerate(batch):
            # Extract generation number from program name, default to 0
            generation_match = re.search(r'gen_(\d+)', code_version.name)
            generation = f"generation_{generation_match.group(1)}" if generation_match else "generation_0"
            
            # Create generation folder
            generation_folder = output_folder / generation
            generation_folder.mkdir(parents=True, exist_ok=True)
            
            # Find corresponding result
            result = None
            # Handle the structure of results from BatchExecutor
            for res_tuple in results:
                if isinstance(res_tuple, tuple) and len(res_tuple) == 2 and res_tuple[0] == code_version.code_version_id:
                    result = res_tuple[1]
                    break
            
            # Create a subfolder for each program using a clean name
            program_folder_name = _make_filesystem_safe(f"{code_version.name}_{code_version.code_version_id[:8]}")
            program_folder = generation_folder / program_folder_name
            program_folder.mkdir(parents=True, exist_ok=True)
            
            # Save code
            code_file = program_folder / "program.py"
            code_file.write_text(code_version.code)
            
            # Save result (including failures!)
            result_file = program_folder / "result.json"
            if isinstance(result, Exception):
                result_data = {"error": "Exception during execution", "exception": str(result), "type": type(result).__name__}
            elif result is not None:
                result_data = result.model_dump()
            else:
                result_data = {"error": "No result found"}
            result_file.write_text(json.dumps(result_data, indent=4))
            
            # Save metadata
            info_file = program_folder / "info.json"
            info_data = {
                "code_version_id": code_version.code_version_id,
                "name": code_version.name,
                "idea": code_version.idea,
                "info": code_version.info if hasattr(code_version, 'info') else {},
                "execution_success": result is not None and not isinstance(result, Exception) and hasattr(result, 'return_code') and result.return_code == 0,
            }
            info_file.write_text(json.dumps(info_data, indent=4))
            
        print_workflow_info(f"💾 Saved {len(batch)} programs to '{output_folder.name}' folder, organized by generation.")


def _make_filesystem_safe(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', name)


def _run_python_code(code: str, python_path: str) -> CodeResult:
    start_time = time.time()
    # write the code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    command = [python_path, temp_file_path]

    # run the command
    logging.info("running command: " + str(command))
    output = subprocess.run(command,
                            capture_output=True,
                            text=True,
                            input="",  # prevents it from blocking on stdin
                            timeout=settings.script_execution_timeout)  # Use centralized timeout
    return_code = output.returncode
    out = output.stdout
    err = output.stderr
    if isinstance(out, str) and out.strip() == "":
        out = None
    if isinstance(err, str) and err.strip() == "":
        err = None

    logging.info("stdout: " + str(out))
    logging.info("stderr: " + str(err))

    # delete the temporary file
    os.remove(temp_file_path)
    runtime_ms = int((time.time() - start_time) * 1000)
    return CodeResult(stdout=out, stderr=err, return_code=return_code, runtime_ms=runtime_ms)


def get_system_info(python_path: str) -> SystemInfo:
    return SystemInfo(
        python_libraries=_get_python_libraries(python_path),
        python_version=_get_python_version(python_path),
        os=sys.platform
    )


def _get_python_libraries(python_path: str) -> list[str]:
    try:
        # Use importlib.metadata to get installed packages (works in all Python 3.8+ environments)
        python_code = """
import importlib.metadata
for dist in importlib.metadata.distributions():
    print(f"{dist.metadata['Name']}=={dist.version}")
"""
        installed_libraries = subprocess.check_output(
            [python_path, "-c", python_code],
            universal_newlines=True
        ).strip()
        return [lib.strip() for lib in installed_libraries.split("\n") if lib.strip()]
    except subprocess.CalledProcessError:
        # If that fails, return empty list
        return []


def _get_python_version(python_path: str) -> str:
    return subprocess.check_output(
        [python_path, "--version"],
        universal_newlines=True
    ).strip()


workflow_runner = _WorkflowRunner()
