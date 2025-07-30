# API Reference

## Animation Classes
This section describes the main animation classes provided by `ez-animate`. Each class is designed to create specific types of animations for different use cases, such as regression, classification, and forecasting.

### RegressionAnimation

Creates Matplotlib animations for regression models.

- Inherits from `AnimationBase`.
- Accepts a regression model, feature matrix `X`, and target vector `y`.
- Supports dynamic and static model parameters, PCA, and plot customization.
- Returns a Matplotlib `FuncAnimation` object for display or saving.

**Constructor:**
```python
RegressionAnimation(
    model,
    X,
    y,
    test_size=0.3,
    dynamic_parameter=None,
    static_parameters=None,
    keep_previous=False,
    max_previous=None,
    pca_components=1,
    metric_fn=None,
    plot_metric_progression=False,
    max_metric_subplots=1,
    **kwargs,
    **kwargs
)
```

#### Parameters:
- `model`: Regression model class (e.g., `LinearRegression`, `SVR`).
- `X`: Feature matrix (2D array-like).
- `y`: Target vector (1D array-like).
- `test_size`: Fraction of data to use for testing (default: 0.3).
- `dynamic_parameter`: Parameter to vary dynamically (e.g., `C` for SVR).
- `static_parameters`: Dictionary of static parameters (e.g., `{'kernel': 'linear'}`).
- `keep_previous`: Whether to keep and display previous model states (default: False).
- `max_previous`: Maximum number of previous states to keep (default: None).
- `pca_components`: Number of PCA components to reduce dimensionality (default: 1).
- `metric_fn`: Optional metric function or list of functions (e.g., MSE, R2) to calculate and display during animation.
- `plot_metric_progression`: Whether to plot the progression of the metric over time.
- `max_metric_subplots`: Maximum number of subplots to show for metric progression (if multiple metrics).
- `**kwargs`: Additional keyword arguments for customization (e.g., `title`, `xlabel`, `ylabel`).


### ClassificationAnimation

Creates Matplotlib animations for classification models.
- Inherits from `AnimationBase`.
- Accepts a classification model, feature matrix `X`, and target vector `y`.
- Supports dynamic/static parameters, PCA, scaling, and plot customization.
- Returns a Matplotlib `FuncAnimation` object for display or saving.

**Constructor:**
```python
ClassificationAnimation(
    model,
    X,
    y,
    test_size=0.3,
    dynamic_parameter=None,
    static_parameters=None,
    keep_previous=False,
    scaler=None,
    pca_components=2,
    plot_step=0.02,
    metric_fn=None,
    plot_metric_progression=None,
    max_metric_subplots=1,
    **kwargs
)
```

#### Parameters:
- `model`: Classification model class (e.g., `LogisticRegression`, `SVC`).
- `X`: Feature matrix (2D array-like).
- `y`: Target vector (1D array-like).
- `test_size`: Fraction of data to use for testing (default: 0.3).
- `dynamic_parameter`: Parameter to vary dynamically (e.g., `C` for SVC).
- `static_parameters`: Dictionary of static parameters (e.g., `{'kernel': 'rbf'}`).
- `keep_previous`: Whether to keep and display previous model states (default: False).
- `scaler`: Scaler instance for preprocessing (e.g., `StandardScaler`).
- `pca_components`: Number of PCA components to reduce dimensionality (default: 2).
- `plot_step`: Step size for mesh grid in decision boundary plots (default: 0.02).
- `metric_fn`: Optional metric function or list of functions (e.g., accuracy, F1) to calculate and display during animation.
- `plot_metric_progression`: Whether to plot the progression of the metric over time.
- `max_metric_subplots`: Maximum number of subplots to show for metric progression (if multiple metrics).
- `**kwargs`: Additional keyword arguments for customization (e.g., `title`, `xlabel`, `ylabel`).



### ClusteringAnimation

Creates Matplotlib animations for clustering models (e.g., K-Means).

- Inherits from `AnimationBase`.
- Accepts a clustering model, input data, and optional true labels.
- Supports dynamic/static parameters, PCA, scaling, cluster center tracing, and plot customization.
- Returns a Matplotlib `FuncAnimation` object for display or saving.

**Constructor:**
```python
ClusteringAnimation(
    model,
    data,
    labels=None,
    test_size=0.3,
    dynamic_parameter=None,
    static_parameters=None,
    keep_previous=False,
    trace_centers=False,
    scaler=None,
    pca_components=2,
    metric_fn=None,
    plot_metric_progression=None,
    max_metric_subplots=1,
    **kwargs
)
```

#### Parameters:
- `model`: Clustering model class (e.g., `KMeans`, `DBSCAN`).
- `data`: Input data for clustering (2D array-like).
- `labels`: Optional true labels for coloring points (1D array-like or list).
- `test_size`: Fraction of data to use for testing (default: 0.3).
- `dynamic_parameter`: Parameter to vary dynamically (e.g., `n_clusters`).
- `static_parameters`: Dictionary of static parameters (e.g., `{'init': 'k-means++'}`).
- `keep_previous`: Whether to keep and display previous cluster assignments/centers (default: False).
- `trace_centers`: Whether to trace the movement of cluster centers over iterations (default: False).
- `scaler`: Scaler instance for preprocessing (e.g., `StandardScaler`).
- `pca_components`: Number of PCA components to reduce dimensionality (default: 2).
- `metric_fn`: Optional metric function or list of functions (e.g., silhouette_score) to calculate and display during animation.
- `plot_metric_progression`: Whether to plot the progression of metrics over frames.
- `max_metric_subplots`: Maximum number of metric subplots to display.
- `**kwargs`: Additional keyword arguments for customization (e.g., `title`, `xlabel`, `ylabel`).


### ForecastingAnimation

Creates Matplotlib animations for time series forecasting models.

- Inherits from `AnimationBase`.
- Accepts a forecasting model, training and test series, and forecast steps.
- Supports dynamic/static parameters and plot customization.
- Returns a Matplotlib `FuncAnimation` object for display or saving.

**Constructor:**
```python
ForecastingAnimation(
    model,
    train_series,
    test_series,
    forecast_steps,
    dynamic_parameter=None,
    static_parameters=None,
    keep_previous=False,
    max_previous=None,
    metric_fn=None,
    plot_metric_progression=None,
    max_metric_subplots=1,
    **kwargs
)
```

#### Parameters:
- `model`: Forecasting model class (e.g., `ARIMA`, `ExponentialSmoothing`).
- `train_series`: Training time series data (1D or 2D array-like).
- `test_series`: Test time series data (1D or 2D array-like).
- `forecast_steps`: Number of steps to forecast at each frame.
- `dynamic_parameter`: Parameter to vary dynamically (e.g., `order` for ARIMA).
- `static_parameters`: Dictionary of static parameters (e.g., `{'trend': 'add'}`).
- `keep_previous`: Whether to keep and display previous forecasts (default: False).
- `max_previous`: Maximum number of previous forecasts to keep (default: None).
- `metric_fn`: Optional metric function or list of functions (e.g., MSE, MAE) to calculate and display during animation.
- `plot_metric_progression`: Whether to plot the progression of metrics over frames.
- `max_metric_subplots`: Maximum number of metric subplots to display.
- `**kwargs`: Additional keyword arguments for customization (e.g., `title`, `xlabel`, `ylabel`).


## Common Methods

All animation classes inherit the following methods:

### setup_plot
```python
setup_plot(title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6))
```
Set up the Matplotlib figure and axes for the animation.

- `title`: Title of the plot.
- `xlabel`: X-axis label.
- `ylabel`: Y-axis label.
- `legend_loc`: Legend location (default: "upper left").
- `grid`: Show grid lines (default: True).
- `figsize`: Figure size (default: (12, 6)).

### animate
```python
animate(frames, interval=150, blit=True, repeat=False)
```
Create the animation using Matplotlib's `FuncAnimation`.

- `frames`: Range or iterable of frames.
- `interval`: Delay between frames in ms (default: 150).
- `blit`: Use blitting for faster rendering (default: True).
- `repeat`: Repeat the animation (default: False).

### save
```python
save(filename, writer="pillow", fps=5, dpi=100)
```
Save the animation to a file (e.g., GIF or MP4).

- `filename`: Output file path.
- `writer`: Animation writer (default: "pillow").
- `fps`: Frames per second (default: 5).
- `dpi`: Dots per inch (default: 100).

### show
```python
show()
```
Display the animation in a window or notebook.
