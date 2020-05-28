library(readxl)
library(reshape2)
library(dplyr)
library(tidyr)
library(fastDummies)
library(qcc)
ebay <- read_excel("eBayAuctions.xls")
train_index <- sample(1:nrow(ebay), 0.6 * nrow(ebay))
train_data <- ebay[train_index,]
test_data <- ebay[-train_index,]

#Function to replace categories in pivot table
pivot_table <- function (pt) {
  pt['merged_column'] = pt[1]
  for (i in 1:(nrow(pt)-1)) {
    for (j in (i+1):nrow(pt)) {
      if ( j <= nrow(pt)) {
        if (abs(pt[i,2] - pt[j,2]) < 0.05) {
          pt[j,3] = pt[i,3]
        }
      }
    }
  }
  return (pt)
}

#Function to replace similar categories in dataset
replace_cols <- function(pt, train_col, test_col, colname){
  for (i in 1:nrow(pt)) {
    train_data[train_col %in% pt[i,1][1], colname] <<- pt[i,3]
    test_data[test_col %in% pt[i,1][1], colname] <<- pt[i,3]
  }
}

#Creating pivot tables
pivot_currency <- train_data %>% 
  select(currency, `Competitive?`) %>%
  group_by(currency) %>%
  summarize(TotalCompetitive = mean(`Competitive?`))
pivot_category <- train_data %>% 
  select(Category, `Competitive?`) %>%
  group_by(Category) %>%
  summarize(TotalCompetitive = mean(`Competitive?`))
pivot_endday <- train_data %>% 
  select(endDay, `Competitive?`) %>%
  group_by(endDay) %>%
  summarize(TotalCompetitive = mean(`Competitive?`))
pivot_duration <- train_data %>% 
  select(Duration, `Competitive?`) %>%
  group_by(Duration) %>%
  summarize(TotalCompetitive = mean(`Competitive?`))


#Creating pivot tables and merging column categories
pt <- pivot_table(pivot_category)
replace_cols(pt = pt, train_col = train_data$Category,
             test_col = test_data$Category, colname = 'Category')
pt <- pivot_table(pivot_currency)
replace_cols(pt = pt, train_col = train_data$currency,
             test_col = test_data$currency, colname = 'currency')
pt <- pivot_table(pivot_endday)
replace_cols(pt = pt, train_col = train_data$endDay,
             test_col = test_data$endDay, colname = 'endDay')
pt <- pivot_table(pivot_duration)
replace_cols(pt = pt, train_col = train_data$Duration,
             test_col = test_data$Duration, colname = 'Duration')

#Creating dummy columns using fastDummies library
train_data1 <- dummy_cols(train_data)


#Fitting model with all the predictors
fit.all <- glm(`Competitive?` ~., family = binomial(link="logit"), data = train_data1)

#Extracting the significant variables
sig_var <- summary(fit.all)$coeff[-1,4] < 0.05
relevant.x <- names(sig_var)[sig_var == TRUE]
significant_predictors <- data.frame(relevant.x)
colnames(significant_predictors) <- "col"
s <- summary(fit.all)$coeff[-1,4]
est <- summary(fit.all)$coefficients[-1, 1]
edf <- data.frame(est)
#Find maximum regression coeffecient
col <- list(summary(fit.all)$coefficients[2:(nrow(edf)+1),0])
col_vec <- unlist(col[[1]])
edf$col <- col_vec
max_reg_coeff <- rownames(edf[which.max(edf$est),])

#Fitting model with the maximum regression coeffecient
fit.single <- glm(`Competitive?` ~., family=binomial(link='logit'), 
                  data=train_data1[c('Competitive?', 'Category_Photography')])



#Fitting the reduced model
fit.reduced <- glm(`Competitive?` ~., family=binomial(link='logit'), 
                   data=train_data1[c('Competitive?', 'Category_Automotive', 'Category_EverythingElse',
                                      'Category_Health/Beauty', 'currency_GBP', 'currency_EUR',
                                      'sellerRating', 'endDay_Mon', 'ClosePrice', 'OpenPrice')])

#Compare both models
anova(fit.reduced, fit.all, test='Chisq')

#Checking for over dispersion
s <- rep(length(train_data1$`Competitive?`), length(train_data1$`Competitive?`))
qcc.overdispersion.test(train_data1$`Competitive?`, size=s, type="binomial")
