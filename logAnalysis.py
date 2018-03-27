#!/usr/bin/env python3
import psycopg2

DBNAME = "news"
NUM_ARTICLES_AUTHORS = 3
PERCENT_THRESHOLD = 1


def get_most_popular_articles_n_authors(num_articles=NUM_ARTICLES_AUTHORS):
    """Returns the views, slug, name, title order by most popular according
    to the log"""
    db = psycopg2.connect(dbname=DBNAME)
    c = db.cursor()
    c.execute("select count(*) as views, name, title " +
              "from log_view_mat " +
              "where slug != '' " +
              "and status = '200 OK' " +
              "group by slug, name, title " +
              "order by views desc " +
              "limit %s", (num_articles,))
    result = c.fetchall()
    db.close()
    return result


def get_days_with_error(percent_error_threshold=PERCENT_THRESHOLD):
    """Returns the day, totalViews and errorViews grouped by day according
    to the log"""
    db = psycopg2.connect(dbname=DBNAME)
    c = db.cursor()
    c.execute("select * from errors_per_day " +
              "where percentage > %s " +
              "order by percentage desc;", (percent_error_threshold,))
    result = c.fetchall()
    db.close()
    return result


def print_result(t, v):
    print('"' + t + '"' + " -", v)


print
print('Most popular articles')
print
articles = get_most_popular_articles_n_authors()
for views, name, title in articles:
    print_result(title, views)

print
print('Most popular authors')
print
authors = get_most_popular_articles_n_authors()
for views, name, title in authors:
    print_result(name, views)

print
print('Days with more than %s%% of error' % PERCENT_THRESHOLD)
print
days_with_error = get_days_with_error()
for day, totalViews, errorViews, percentage in days_with_error:
    print(day.strftime('%B %d, %Y') + " -",  round(percentage, 2), "%")
print
