"DATASCI217 Final Exam, Question 3"

import pandas as pd
from scipy import stats
import statsmodels.api as sm
import numpy as np
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.anova import anova_lm

def main():
    # Load cleaned CSV file
    df = pd.read_csv("updated_ms_data.csv")

    # Convert to correct types
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    df["education_level"] = df["education_level"].astype('category')
    # Set the order of the education categories
    df["education_level"] = df["education_level"].cat.set_categories(['High School', 'Some College', 'Bachelors', 'Graduate'],
                                                                     ordered=True)
    df["insurance_type"] = df["insurance_type"].astype('category')

    # Check for outliers for walking_speed
    z_score = np.abs(stats.zscore(df['walking_speed']))
    outliers_walking_speed = df[z_score > 3]
    print(f"Walking speed outliers count: {len(outliers_walking_speed)}")

    # Analyze walking speed (No need to handle outliers, only 2 outliers present)
    # Multiple regression with education and age 
    age_education_result1 = sm.OLS.from_formula("walking_speed ~ age + education_level",
                                                 data = df).fit()
    
    # To Account for repeated measures, Mixedlm can be used 
    age_education_result2 = sm.MixedLM.from_formula("walking_speed ~ age + education_level",
                                                    data = df,
                                                    groups = "patient_id").fit(maxiter = 5000, 
                                                                               method='powell', 
                                                                               reml=False)
    
    # Test for significant trends
    walking_anova_result = anova_lm(age_education_result1, type = 2)

    # Check for outliers for visit_cost
    z_score = np.abs(stats.zscore(df['visit_cost']))
    outliers_visit_cost = df[z_score > 3]
    print(f"Visit cost outliers count: {len(outliers_visit_cost)}")

    # Analyze costs (No need to handle outliers, since there is no outliers)
    # Simple analysis of insurance type effect
    cost_result = sm.OLS.from_formula("visit_cost ~ insurance_type", 
                                      data = df).fit()

    # Basic statistics
    print(f"Basic statistics of visit cost by insurance type: {df.groupby('insurance_type')['visit_cost'].describe()}")
    cost_anova_result = anova_lm(cost_result, type = 2)
  

    # Calculate effect sizes
    # Extract sums of squares
    ss_total = cost_anova_result['sum_sq'].sum()
    ss_factor = cost_anova_result.loc['insurance_type', 'sum_sq']

    # Calculate Eta Squared
    eta_squared = ss_factor / ss_total

    # Advanced analysis 
    # Education age interaction effects on walking speed
    # Control for relevant confounders
    interaction_result = sm.OLS.from_formula("walking_speed ~ age * education_level + insurance_type + visit_cost", 
                                             data = df).fit()
    
    # Report key statistics, coefficients, p-values and confidence intervals
    with open("README.md", "a") as file:
        file.write("\n")
        print(f"## **Question 3**", file = file)
        print(f"**Regression model of education and age effect on walking speed:**\n", file = file)

        # Extract statistics
        coefficients = age_education_result1.params
        conf_intervals = age_education_result1.conf_int()
        p_values = age_education_result1.pvalues
        for var in coefficients.index:
            coef = coefficients[var]
            ci_lower, ci_upper = conf_intervals.loc[var]
            p_val = p_values[var]
            print(f"- {var} coefficient = {coef:.2f}, 95% CI[{ci_lower:.2f}, {ci_upper:.2f}], p-value = {p_val:.2f}", file = file)
        
        file.write("\n")
        print(f"**Regression model of education level and age effect on walking speed (accounting for repeated measures):**\n", file = file)

        # Fixed effects summary
        fixed_effects = age_education_result2.params
        conf_intervals = age_education_result2.conf_int()
        p_values = age_education_result2.pvalues

        # Format results for fixed effects
        fixed_effects_lines = []
        for var in fixed_effects.index:
            coef = fixed_effects[var]
            ci_lower, ci_upper = conf_intervals.loc[var]
            p_val = p_values[var]
            print(f"- {var} coefficient = {coef:.2f}, 95% CI[{ci_lower:.2f}, {ci_upper:.2f}], p-value = {p_val:.2f}", file = file)
        
        file.write("\n")
        print(f"**ANOVA of walking speed based on age and education level:**\n", file = file)
        
        # Format results
        for index, row in walking_anova_result.iterrows():
            f_stat = row['F']
            p_val = row['PR(>F)']
            print(f"- {index} F = {f_stat:.2f}, p-value = {p_val:.2f}", file = file)
        
        file.write("\n")
        print(f"**Regression model of insurance type effect on visit cost:**\n", file = file)

        # Extract statistics
        coefficients = cost_result.params
        conf_intervals = cost_result.conf_int()
        p_values = cost_result.pvalues
        for var in coefficients.index:
            coef = coefficients[var]
            ci_lower, ci_upper = conf_intervals.loc[var]
            p_val = p_values[var]
            print(f"- {var} coefficient = {coef:.2f}, 95% CI[{ci_lower:.2f}, {ci_upper:.2f}], p-value = {p_val:.2f}", file = file)
        
        file.write("\n")
        print(f"**ANOVA of visit cost based on insurance type:**\n", file = file)
        
        # Format results
        for index, row in cost_anova_result.iterrows():
            factor_df = row['df']
            residual_df = cost_anova_result.loc['Residual', 'df']  
            f_stat = row['F']
            p_val = row['PR(>F)']
            print(f"- {index} F = {f_stat:.2f}, p-value = {p_val:.2f}", file = file)
        file.write("\n")
        print(f"- The effect size (Eta Squared) of insurance type is {eta_squared:.2f}, indicating that "
              f"{eta_squared * 100:.2f}% of the variance in visit cost is explained by insurance type.", file = file)

        file.write("\n")
        print(f"**Regression model of education and age interaction and other confounders effect on walking speed:**\n", file = file)

        # Extract key statistics
        coefficients = interaction_result.params
        conf_intervals = interaction_result.conf_int()
        p_values = interaction_result.pvalues
        r_squared = interaction_result.rsquared
        adj_r_squared = interaction_result.rsquared_adj
        aic = interaction_result.aic
        bic = interaction_result.bic

        for var in coefficients.index:
            coef = coefficients[var]
            ci_lower, ci_upper = conf_intervals.loc[var]
            p_val = p_values[var]
            print(f"- {var} Coefficient = {coef:.2f} (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}], p-value = {p_val:.2f})", file = file)

if __name__ == "__main__":
    main()