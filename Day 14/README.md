# Day 14 - NLP Sentiment Analysis using Hugging Face Transformers
## Project Objective
The objective of this project was to perform sentiment analysis on customer reviews using a pre-trained Large Language Model (LLM) from Hugging Face Transformers. The reviews were cleaned using Regular Expressions and classified into sentiment categories without training a new model.
## Dataset
- Womens Clothing E-Commerce Reviews Dataset
## Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Regular Expressions (Regex)
- Hugging Face Transformers
- PyTorch
## Project Workflow
1. Loaded the customer reviews dataset.
2. Cleaned review text using Regular Expressions.
3. Loaded a pre-trained Hugging Face sentiment analysis model.
4. Performed sentiment analysis on customer reviews.
5. Added Predicted_Sentiment and Confidence_Score columns.
6. Visualized sentiment distribution using a count plot.
7. Exported the final dataset with predictions.
## Output Files
- nlp_sentiment_wrapper.ipynb
- customer_reviews_with_sentiment.csv
- requirements.txt
- README.md
## Conclusion
This project demonstrated how pre-trained Large Language Models can perform accurate sentiment analysis without requiring model training or fine-tuning. Hugging Face Transformers provide an efficient way to apply NLP models to real-world text data.