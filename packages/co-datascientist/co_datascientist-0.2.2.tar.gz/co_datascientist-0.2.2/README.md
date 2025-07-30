# CoDatascientist

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

<!-- TODO: new liscnece! -->

<div align="center">
  <img src="figures/logo2.png" alt="PiñaColada Logo" width="500"/>
</div>

An agentic framework for recursive model improvement.

</div>

## 🚀 Quickstart
Install `co-datascientist`:

```bash
pip install co-datascientist
```

To use from command line, run:
```bash
co-datascientist run --script-path myscript.py
```

To use from cursor or other AI clients, run the MCP server:
```bash
co-datascientist mcp-server
```

And add the MCP configuration to the AI client. For example in cursor go to:
`file -> preferences -> cursor settings -> MCP -> Add new global MCP server`,
and add the co-datascientist mcp server config in the json, should look like this:
```json
{
  "mcpServers": {
    "CoDatascientist": {
        "url": "http://localhost:8000/sse"
    }
  }
}
```

## 🎯 **IMPORTANT: KPI Tagging for Smart Organization**

> **⚠️ Required for automatic folder organization!**

CoDatascientist automatically organizes your results by performance when you add a simple **KPI tag** to your script:

```python
# At the end of your script, add this line:
print(f"KPI: {your_metric:.4f}")
```

### Examples:
```python
# For accuracy
accuracy = accuracy_score(y_true, y_pred)
print(f"KPI: {accuracy:.4f}")  # → folder named "0_9234_your_idea"

# For F1 score
f1 = f1_score(y_true, y_pred)
print(f"KPI: {f1:.4f}")       # → folder named "0_8567_your_idea"

# For custom metrics
custom_score = (accuracy + f1) / 2
print(f"KPI: {custom_score:.4f}")  # → folder named "0_8901_your_idea"
```

### 📁 **What This Does:**
- **Without KPI**: Folders named `baseline/`, `random_forest_idea/`
- **With KPI**: Folders named `0_92_baseline/`, `0_87_random_forest_idea/`
- **Result**: Instantly see which ideas perform best! 🚀

### 📋 **Supported Formats:**
- `KPI: 0.85` ✅
- `kpi: 0.95` ✅ (case insensitive)
- `KPI:0.77` ✅ (no space)
- If no KPI found → uses original naming (safe fallback)

## 🔑 Adding Your OpenAI API Key

CoDatascientist supports using your own OpenAI API key for unlimited usage (instead of the free tier). You can manage your OpenAI key through the CLI:

### Add/Update OpenAI Key
```bash
# This will prompt you to enter your OpenAI API key
co-datascientist --reset-openai-key run --script-path myscript.py
```

Or use the dedicated key management command:
```bash
# Manage your OpenAI key
co-datascientist openai-key
```

### Remove OpenAI Key
```bash
# Switch back to free tier
co-datascientist openai-key --remove
```

### Check Current Status
```bash
# See if you're using your OpenAI key or the free tier
co-datascientist status
```

**Benefits of adding your OpenAI key:**
- 🚀 **Unlimited usage** with your OpenAI account
- 💰 **Direct billing** to your OpenAI account  
- 🔒 **No usage limits** from TropiFlow's free tier

**Note**: Get your OpenAI API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## 💰 Cost Tracking
Track your LLM usage costs automatically:

```bash
# View summary costs
co-datascientist costs

# View detailed breakdown
co-datascientist costs --detailed
```

The system automatically tracks:
- **Total costs** across all workflows
- **Token usage** (input/output tokens)
- **Per-workflow costs** and breakdown
- **Model-specific costs** using LiteLLM's built-in pricing

All costs are calculated in real-time using LiteLLM's `completion_cost()` function with up-to-date pricing for all supported models (OpenAI, Anthropic, DeepSeek, etc.).


## 📝 Example: Before vs After

See how CoDatascientist transforms simple ML code into sophisticated, mathematically-grounded solutions:

<table>
<tr>
<th>📥 Input Code</th>
<th>📤 Enhanced Output</th>
</tr>
<tr>
<td>

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import numpy as np

# XOR data
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 1, 1, 0])

# Define pipeline: preprocessing + model
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=10, random_state=0))
])

# Fit
pipeline.fit(X, y)

# Predict and evaluate
preds = pipeline.predict(X)
accuracy = accuracy_score(y, preds)
print(f"Accuracy: {accuracy:.2f}")

# 🎯 IMPORTANT: Add this KPI tag for automatic folder organization
print(f"KPI: {accuracy:.4f}")
```

</td>
<td>

```python
import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from tqdm import tqdm

class ChebyshevPolyExpansion(BaseEstimator, TransformerMixin):
    def __init__(self, degree=3):
        self.degree = degree
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        X = np.asarray(X)
        X_scaled = 2 * X - 1
        n_samples, n_features = X_scaled.shape
        features = []
        for f in tqdm(range(n_features), desc="Chebyshev features"):
            x = X_scaled[:, f]
            T = np.empty((self.degree + 1, n_samples))
            T[0] = 1
            if self.degree >= 1:
                T[1] = x
            for d in range(2, self.degree + 1):
                T[d] = 2 * x * T[d - 1] - T[d - 2]
            features.append(T.T)
        return np.hstack(features)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 1, 1, 0])

pipeline = Pipeline([
    ('cheb', ChebyshevPolyExpansion(degree=3)),
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=10, random_state=0))
])

pipeline.fit(X, y)

preds = pipeline.predict(X)
accuracy = accuracy_score(y, preds)
print(f"Accuracy: {accuracy:.2f}")

# 🎯 IMPORTANT: Add this KPI tag for automatic folder organization
print(f"KPI: {accuracy:.4f}")
```

</td>
</tr>
</table>


### Cost Management
- 💰 Real-time cost tracking per user
- 📊 Token usage monitoring
- 🔍 Workflow-level cost breakdown
- 📈 Model-specific cost analysis


## Any questions? Contact us!
we're happy to help, discuss and debug.

contact us at `oz.kilim@tropiflo.io`

---
<div align="center">
Made with ❤️ by the Tropiflo team
</div>