# Code for supplementary figure 3

library(data.table)
library(margins)
library(lmtest)
library(ggplot2)
library(gridExtra)
library(ggeffects)
library(stargazer)
library(coefplot)
library(pROC)
library(ROCR)
library(dplyr)
library(caret)

df1=fread('aseg.vol.table')
df1 <- df1 %>%
  rename(participant_id = 'Measure:volume') %>%
  rename(`RightAmygdala` = 'Right-Amygdala') %>%
  rename(`LeftAmygdala` = 'Left-Amygdala') %>%
  rename(`RightHippocampus` = 'Right-Hippocampus') %>%
  rename(`WMHyperintensities` = 'WM-hypointensities') %>%
  rename(`LeftHippocampus` = 'Left-Hippocampus') %>%
  mutate(participant_id = gsub('sub-|_recon', '', participant_id))

df1$ventricles <-rowSums(df1[,c('Left-Lateral-Ventricle',
                                'Right-Lateral-Ventricle',
                                'Left-Inf-Lat-Vent',
                                'Right-Lateral-Ventricle'
                                )])
df1$Hippocampus <-rowMeans(df1[,c('RightHippocampus', 'LeftHippocampus')])
df1$Amygdala <-rowMeans(df1[,c('RightAmygdala', 'LeftAmygdala')])

df1$CortexVol <-rowMeans(df1[,c('lhCortexVol', 'rhCortexVol')])
df1$TotalBrain <- rowSums(df1[,c('CerebralWhiteMatterVol',
                                 'TotalGrayVol'
                                  )])

df1$CerebralWhiteMatterVol <- scale(log(df1[,c('CerebralWhiteMatterVol')]))
df1$ratio_Hippocampus_TotalGrayVol <- scale(df1[,c('Hippocampus')]/df1[,c('TotalGrayVol')])
df1$ratio_GreyMatterVolume_EstimatedTotalIntraCranialVol <- scale(df1[,c('TotalGrayVol')]/df1[,c('EstimatedTotalIntraCranialVol')])
df1$WMHyperintensities <- scale(df1[,c('WMHyperintensities')])

df=fread('stats_model_data_adj_R6.csv') # average PSD over all sensors, MMSE adj

df_converter=df[group=='patient']
df_converter=df[!is.na(Converters)]

merged_df <- merge(df1, df_converter, by = 'participant_id', all = FALSE)
merged_df$participant_id <- NULL
write.csv(merged_df, "merged_df.csv", row.names = FALSE)

#MOD1
mod1 <- glm(Converters ~ scale(age) + scale(Edu_years) + scale(MMSE) , data = merged_df, family = binomial)
summary(mod1)
summary(margins(mod1))
summary_marg_mod1 <-summary(margins(mod1))
write.csv(summary_marg_mod1, "mod1_age_edu_mmse.csv", row.names = FALSE)

#MOD2
mod2 <- glm(Converters ~ scale(age) + scale(Edu_years) + scale(MMSE) + ratio_Hippocampus_TotalGrayVol, data = merged_df, family = binomial)
summary(mod2)
summary(margins(mod2))
summary_marg_mod2 <-summary(margins(mod2))
write.csv(summary_marg_mod2, "mod2_age_edu_mmse_Hipp_ratio.csv", row.names = FALSE)

# MOD3
mod3 <- glm(Converters ~ scale(age) + scale(Edu_years) + scale(MMSE) + scale(meg_average_adj), data = merged_df, family = binomial(link="logit"))
summary(mod3)
summary(margins(mod3))
summary_marg_mod3 <-summary(margins(mod3))
write.csv(summary_marg_mod3, "mod3_age_edu_mmse_MEGaverage.csv", row.names = FALSE)

# MOD4
mod4 <- glm(Converters ~ scale(age) + scale(Edu_years) + scale(MMSE) + scale(meg_average_adj) + ratio_Hippocampus_TotalGrayVol, data = merged_df, family = binomial(link="logit"))
summary(mod4)
summary(margins(mod4))
summary_marg_mod4 <-summary(margins(mod4))
write.csv(summary_marg_mod4, "mod4_age_edu_mmse_MEGaverage.csv", row.names = FALSE)

# compare models
AIC(mod1, mod2, mod3, mod4)
AIC_diff <-AIC(mod1, mod2, mod3, mod4)
diff(AIC_diff$AIC)

# PLOT AUC
# ROC data
roc_data_mod1 <- roc(merged_df$Converters, predict(mod1, type = "response"))
roc_coordinates <- coords(roc_data_mod1, "all")
write.csv(roc_coordinates, "roc_data_mod1.csv", row.names = FALSE)

roc_data_mod2 <- roc(merged_df$Converters, predict(mod2, type = "response"))
roc_coordinates <- coords(roc_data_mod2, "all")
write.csv(roc_coordinates, "roc_data_mod2.csv", row.names = FALSE)

roc_data_mod3 <- roc(merged_df$Converters, predict(mod3, type = "response"))
roc_coordinates <- coords(roc_data_mod3, "all")
write.csv(roc_coordinates, "roc_data_mod3_MEG_average.csv", row.names = FALSE)

roc_data_mod4 <- roc(merged_df$Converters, predict(mod4, type = "response"))
roc_coordinates <- coords(roc_data_mod4, "all")
write.csv(roc_coordinates, "roc_data_mod4_MEG_average.csv", row.names = FALSE)

# Compute sensitivity, specificity, AUC, Accuracy
predicted_labels <- ifelse(predict(mod4, type = "response") > 0.5, 1, 0)
actual_labels <- merged_df$Converters

true_positives <- sum(predicted_labels == 1 & actual_labels == 1)
false_negatives <- sum(predicted_labels == 0 & actual_labels == 1)
true_negatives <- sum(predicted_labels == 0 & actual_labels == 0)
false_positives <- sum(predicted_labels == 1 & actual_labels == 0)

sensitivity_mod4 <- true_positives / (true_positives + false_negatives)
specificity_mod4 <- true_negatives / (true_negatives + false_positives)
accuracy_mod4 <- (true_positives + true_negatives) / (true_positives + true_negatives + false_positives + false_negatives)
auc_mod4 <- auc(roc_data_mod4)

print(accuracy_mod4)
print(auc_mod4)
print(sensitivity_mod4)
print(specificity_mod4)

###### BOOTSTRAP REAMPLING FOR IC95 AUC

# Number of bootstrap samples
n_boot <- 2000

# Create an empty list to store bootstrapped AUC values for each model
boot_auc_values <- list()

# Bootstrap AUC Calculation Function
bootstrap_auc <- function(model, data, response_col) {
  set.seed(123)
  aucs <- numeric(n_boot)
  for (i in 1:n_boot) {
    # Resample the data (with replacement)
    resampled_data <- data[sample(nrow(data), replace = TRUE), ]
    
    # Refit the model on the resampled data
    resampled_model <- glm(formula = model$formula, data = resampled_data, family = binomial)
    
    # Get predicted probabilities
    resampled_probs <- predict(resampled_model, type = "response")
    
    # Calculate ROC and AUC
    roc_resampled <- roc(resampled_data[[response_col]], resampled_probs)
    aucs[i] <- auc(roc_resampled)
  }
  return(aucs)
}

# Run bootstrap for each model
boot_auc_values$Model_1 <- bootstrap_auc(mod1, merged_df, "Converters")
boot_auc_values$Model_2 <- bootstrap_auc(mod2, merged_df, "Converters")
boot_auc_values$Model_3 <- bootstrap_auc(mod3, merged_df, "Converters")
boot_auc_values$Model_4 <- bootstrap_auc(mod4, merged_df, "Converters")

# differences of AUCs
diff_aucMod4Mod3 <- (boot_auc_values$Model_4 - boot_auc_values$Model_3)
hist(diff_aucMod4Mod3)

diff_aucMod4Mod2 <- (boot_auc_values$Model_4 - boot_auc_values$Model_2)
hist(diff_aucMod4Mod2)

# Calculate the difference in 95% confidence intervals for each model
ci_diff_aucMod4Mod3 <- quantile(diff_aucMod4Mod3, probs = c(0.025, 0.975))
ci_diff_aucMod4Mod2 <- quantile(diff_aucMod4Mod2, probs = c(0.025, 0.975))
ci_diff_aucMod4Mod1 <- quantile(diff_aucMod4Mod1, probs = c(0.025, 0.975))

# Calculate the 95% confidence intervals for each model
ci_model1 <- quantile(boot_auc_values$Model_1, probs = c(0.025, 0.975))
ci_model2 <- quantile(boot_auc_values$Model_2, probs = c(0.025, 0.975))
ci_model3 <- quantile(boot_auc_values$Model_3, probs = c(0.025, 0.975))
ci_model4 <- quantile(boot_auc_values$Model_4, probs = c(0.025, 0.975))

# Print the confidence intervals
print(ci_model1)
print(ci_model2)
print(ci_model3)
print(ci_model4)