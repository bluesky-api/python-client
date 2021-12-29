import blueskyapi


client = blueskyapi.Client()

d = client.latest_forecast(
    53,
    10,
    columns=["wind_u_at_100m"],
    forecast_distances=[0, 24],
)
print(d)


d = client.forecast_history(
    53,
    10,
    columns=["wind_u_at_100m"],
    forecast_distances=[0, 24],
    min_forecast_moment="2021-06-01 00:00",
)
print(d)
