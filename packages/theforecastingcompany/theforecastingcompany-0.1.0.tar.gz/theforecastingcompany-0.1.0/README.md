# The Forecasting Company Python SDK

[![PyPI version](https://img.shields.io/pypi/v/theforecastingcompany)](https://pypi.org/project/theforecastingcompany/)
[![API status](https://api.checklyhq.com/v1/badges/groups/2038018?style=flat&theme=default)](https://status.retrocast.com)

The python SDK provides a simple interface to make forecasts using the TFC API.

## Documentation

The REST API documentation can be found on [https://api.retrocast.com/docs](https://api.retrocast.com/docs).

To get an API key, visit the [Authentication docs](https://api.retrocast.com/docs/routes#authentication). In the **API Keys** section you will find an option to _Sign in_ or, if you already signed in, a box containing your API key.

## Installation

```sh
# install from PyPI
pip install theforecastingcompany
```

## Usage

```python
# By default it will look for api_key in os.getenv("TFC_API_KEY"). Otherwise you can explicity set the api_key argument
client = TFCClient()

# Compute forecast for a single model
timesfm_df = client.forecast(
    train_df,
    model=TFCModels.TimesFM_2 # StrEnum defined in utils. You can also pass the model name as a string, eg timesfm-2
    horizon=12,
    freq="W",
)

# Global Model with static variables
tabpfn_global_df = client.forecast(
        train_df,
        model=TFCModels.TFCGlobal,
        horizon=12,
        freq="W",
        static_variables=["unique_id","Group","Vendor","Category"],
        add_holidays=True,
        add_events=True,
        country_isocode = "US"
    )
```

If future_variables are available, make sure to pass also a `future_df` when forecasting, and setting the `future_variables` argument. All future variables must be present in the `future_df`.

The `cross_validate` function is basically the same, but takes a `fcds` argument to define the FCDs to use for cross-validation. It also returns the target column in the output dataframe. 

`train_df` and `future_df` should have `id_col` (default "unique_id"), `date_col` (default "ds"), and `target_col` (default "target"). You can set the corresponding arguments if column names are different from default ones.

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```py
import theforecastingcompany
print(theforecastingcompany.__version__)
```

## Requirements

Python 3.11 or higher.
