import pandas as pd

df = pd.read_csv('../post-processing/comments.csv')

small_df = pd.DataFrame(columns=['comment_id', 'text', 'collected_at', 'published_at', 'reply_to'])
counter = {}

for i, row in df.iterrows():
  if row.comment_id.split('-')[1] == '0':
    small_df = small_df.append(row)
  elif row.reply_to not in counter:
    small_df = small_df.append(row)
    counter[row.reply_to] = 1
  elif counter[row.reply_to] < 10:
    small_df = small_df.append(row)
    counter[row.reply_to] += 1

small_df.to_csv('comments-small.csv', index=False)