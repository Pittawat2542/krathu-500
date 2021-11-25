# krathu-500
A dataset of post-comment on Pantip, a popular Thai web board.

## Project Structure

`main.py` hosts all web crawler code for both posts and comments.
`example/` folder hosts an example on how to use dataset with machine learning techniques with result. Inside the folder also contains the result of the program.
`post-processing/` folder hosts post-processing script and result.
`small-dataset-generator/` folder contains utility script for generating a small version of dataset.
`labeled/` folder contains labeled data.
`baseline-model/` contains code for three basedline model (LSTM, CNN, BERT) trained on the labeled dataset.

## Dataset file
The final version of the datasets is located at `post-processing/posts.csv` and `post-processing/comments.csv`. You can also grab the unprocessed version of the dataset at `posts.csv` and `comments.csv`.

There are labeled version of small dataset located at `labeled/comments-small-labeled.csv`. The small version of comments selected the first ten comments of each posts. It has a classification label for sentiment of the text by considering the post body context. The class labels are `NEU` for neutral, `NEG` for negative, and `POS` for positive comments.

### Label explanation
There are three possible labels for setiment labeling. POS for positive comments, NEU for neutral comments, and NEG for negative comments.

#### POS (Positive)
- Good vibe
- Expressing gratitude
- Encouraging people
- Optimistic comment

#### NEG (Negative)
- Containing bad words
- Expressing anger, sadness
- Discouraging people
- Pessimistic comment

#### NEU (Neutral)
- Discussion/Explanation without emotion
- Tell a story
- Mixture of positive and negative stories
- Does not belong to either POS or NEG

## Annotator Agreement
You can help contribute to the annotated corpus by either

1. Annotate other parts of the dataset
2. Re-annotate the annotated dataset for cross checking

Please also to the `Label explanation` section above for more

## Contribution

Please feel free to open any pull requests for contributing to the repository either fixing bugs, add more model, or add more data.
