"""DATASCI217 Final Exam, Question 2"""

# Import libraries
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.regression.linear_model import OLS
import statsmodels.api as sm

def main():
    random.seed(42)
    # Load cleaned CSV file
    df = pd.read_csv("ms_data.csv")
    # Convert visit_date to datetime
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    # Sort by patient_id and visit_date
    df = df.sort_values(by = ["patient_id", "visit_date"])

    # Read insurance types from insurance.lst
    with open("insurance.lst", "r") as file:
        # Save insurance types in insurance_types list
        insurance_types = []
        for line in file:
            insurance_types.append(line.strip())

        # Create a dataframe with unique patient_ids 
        # Random insurance types assignments to each patient
        insurance_df = pd.DataFrame({
            "patient_id": df["patient_id"].unique(),
            "insurance_type": np.random.choice(insurance_types, size = len(df["patient_id"].unique()), replace=True)
            })
    # Add insurance info to the original dataframe
    df = df.merge(insurance_df, on = "patient_id", how = "left")

    # Generate plan costs for each insurance type
    insurance_cost = {"Basic": 100, "Premium": 150, "Platinum": 200}
    # Add visit_cost values based on insurance type and adding a random variation 
    df["visit_cost"] = df["insurance_type"].apply(lambda x: insurance_cost[x] + np.random.normal(0, 10)).round(2)

    # Handle the data
    # Convert education_level column to a category
    df["education_level"] = df["education_level"].astype('category')

    # Check missing values
    print(f"Missing values:\n{df.isna().sum()}")
    # No need to handle missing values, since there are none

    # Save the structurs dataframe as a csv file
    df.to_csv("updated_ms_data.csv", index=False)

    # Mean walking speed by education level
    walk_speed_result = df.groupby("education_level")["walking_speed"].mean()

    # Mean costs by insurance type
    cost_result = df.groupby("insurance_type")["visit_cost"].mean()

    # Age effects on walking speed
    # Fit linear regression model to find age effect on walking_speed
    X_with_const = sm.add_constant(df['age'])
    model = OLS(df['walking_speed'], X_with_const)
    age_result = model.fit()

    # Create a dataframe with datetimeIndex (visiting_date column) and walking_speed and age columns 
    # Resample visit_dates into monthly manner
    time_index_df = df[["walking_speed", "age", "visit_date"]].set_index('visit_date').resample('ME').mean()

    time_index_df['walking_speed'] = time_index_df['walking_speed'].interpolate(method='linear')

    # Decompose the trend by extracting a repeated seasonal pattern over a 12-month period
    decomposition = seasonal_decompose(time_index_df['walking_speed'], model='additive', period = 12)

    # Plot walking speed time series 
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize = (10, 10))
    time_index_df['walking_speed'].plot(ax = ax1, title = 'Original')
    decomposition.trend.plot(ax = ax2, title = 'Trend')
    decomposition.seasonal.plot(ax = ax3, title = 'Seasonal')
    decomposition.resid.plot(ax = ax4, title = 'Residual')
    plt.tight_layout()
    # Save the plot as an image
    plot_path = "Age_trend_plot.png"
    plt.savefig(plot_path)
    plt.close()

    # Add summary statistics into the readme.md
    with open("README.md", "a") as file:
        file.write("\n")
        print(f"## **Question 2**", file = file)
        print(f"**Mean walking speed by education level:**\n", file = file)
        for index, value in sorted(walk_speed_result.items(), key = lambda x: x[1]):
            print(f"- {index}: {value}\n", file = file)
        print(f"**Mean costs by insurance type:**\n", file = file)
        for index, value in sorted(cost_result.items(), key = lambda x: x[1]):
            print(f"- {index}: {value}\n", file = file)
        print(f"**Linear regression model for age effect on walking speed:**\n", file = file)
        print(f"- Age coefficient: {age_result.params['age']:.2f}\n", file = file)
        print(f"- P-value: {age_result.pvalues['age']:.2f}\n", file = file)
        print(f"- R-squared: {age_result.rsquared:.2f}\n", file = file)
        print(f"**Walking speed trend over time (Decomposition plot):**\n", file = file)
        print(f"![Decomposition Plot]({plot_path})\n", file = file)

if __name__ == "__main__":
    main()