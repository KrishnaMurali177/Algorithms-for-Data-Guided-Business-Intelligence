# Algorithms for Data Guided Business Intelligence
Data driven projects with sample business applications done for the course CSC 590.

## Data Wrangling with Python and Pandas
Project on handling data -- Data cleaning, Exploratory data analysis and data manipulation. 

## Music Recommender System using Aletrnating Least Squares in Apache Spark
Performing EDA on RDDs in Spark and Implementing the ALS algorithm in Apache Spark to recommend the top artists a user would listen to according to their previous songs listened data. 

## Bitcoin Price Prediction
Using Bayesian regression to predict the price of bitcoins based on previous data. Implementing the theory presented in the [paper](https://arxiv.org/pdf/1410.1231.pdf), we choose parameters and close in on the regression coeefecients for predicting bitcoin prices.

## Deep Neural Network Architectures for defect detection
Detecting defects on textured surfaces using Image segmentation to detect the pixels where the defect occurs in the given image. 
Dataset - https://hci.iwr.uni-heidelberg.de/content/weakly-supervised-learning-industrial-optical-inspection
Implementing the approach given in the [paper](https://arxiv.org/abs/1505.04597)

## Generalized Linear Models - Logistic regression
Build and analyze a logistic regression model in R using all the features as predictors. Scrutinize the model by reducing predictors according to significance and combining predictors to produce a better model

## DeepWalk: Multipartite Graph Embedding for Recommender Systems
Predict a user’s preference for some item they have not yet rated using a collaborative filtering graph-based technique called DeepWalk. The main steps are:
- Create a heterogeneous information network with nodes consisting of users, item- ratings, items, and other entities related to those items
- Use DeepWalk to generate random walks over this graph
- Based on these random walks, embed the graph in a low dimensional space using word2vec. Evaluate and compare preference propagation algorithms in heterogeneous information networks generated from user-item relationships. Implement and evaluate a word2vec-based method.

## Market Segmentation and Influence Propagation
Market segmentation divides a broad target market into subsets of consumers or businesses that have or are perceived to have common needs, interests, and priorities. In this project, we aim to find such market segments given social network data. These social relations can be captured in a graph framework where nodes represent customers/users and edges represent some social relationship. The properties belonging to each customer/user can be treated as node attributes. Hence, market segmentation becomes the problem of community detection over attributed graphs, where the communities are formed based on graph structure as well as attribute similarities. We evaluate the obtained segments via influence propagation (influence an entity in each segment and measure how fast the influence propagates over the entire network).

## Network Properties for Apache Spark
Implement various network properties using pySpark, GraphFrames and networkx:
- Degree Distribution: a measure of the frequency of nodes that have a certain degree
- Centrality: determine nodes that are important based on the structure of the graph. Closeness centrality measures the distance of a node to all other nodes.
- Articulation Points: vertices in the graph that, when removed, create more components than there were originally.

## Stochastic Gradient Descent
Implementing Stochastic Gradient Descent in Linear Regression with L-2 Regularization

## Supervised Learning Techniques for Sentiment Analytics
Perform sentiment analysis over IMDB movie reviews and Twitter data to classify tweets or movie reviews as either positive or negative given a labeled training data to build the model and labeled testing data to evaluate the model. Generate embedding/feature vectors using Word2Vec and Doc2Vec techniques and build classifiers using logistic regression as well as a Naive Bayes classifier.

## Twitter Sentiment Analytics with Spark Streaming
Perform sentiment analytics on real time tweets using Apache Kafka and Spark
