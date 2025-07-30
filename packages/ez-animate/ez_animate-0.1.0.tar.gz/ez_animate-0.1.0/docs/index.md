# ez-animate

A high-level, declarative Python package for creating common Matplotlib animations with minimal boilerplate code.

## Project Goals

- **Simplify Matplotlib animations**: No need to write custom `init`/`update` functions or manage state manually.
- **For data scientists, analysts, educators, and researchers**: Quickly create standard animations for analysis, presentations, and teaching.
- **Minimal code, maximum clarity**: Focus on your data and story, not boilerplate.

See the navigation for installation, usage, API, and contribution details.

## Example Animations
### Regression Animation with SGD
This animation demonstrates SGD regression, showing how the model fits the data as the *max_iter* parameter increases. You can see how the model's predictions with each iteration change, and how the metrics evolve over time.
![SGD Regression Animation](plots/animator_sgd.gif)

### Exponential Moving Average Forecast Animation
This animation illustrates how the Exponential Moving Average (EMA) forecast evolves over time, highlighting the smoothing effect of different *alpha* values.
![Exponential Moving Average Forecast Animation](plots/animator_ema_forecast.gif)

### Clustering Animation with KMeans
This animation visualizes KMeans clustering, showing how the centroids and clusters change as the number of iterations increases, showcasing the algorithm's convergence process.
![KMeans Clustering Animation](plots/animator_kmeans.gif)
