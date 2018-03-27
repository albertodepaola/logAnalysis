# Log Analysis

This project is a simple log analysis tool that answers 3 questions: 
- What are the most popular three articles of all time?
- Who are the most popular article authors of all time?
- On which days did more than 1% of requests lead to errors?

The number of articles, authors and the threshold percentage are configurable in constants in the main script.

# Installation

In order to run the code, python 3.5 or greater is required. Check this [guide](https://wiki.python.org/moin/BeginnersGuide) to install it on your system of choice.

This simple views were created in order to accelerate and simplify the main queries. In order to run the script, this sql snippets should
be executed in the news database.

```SQL
create materialized view log_view_mat as
select l.*, a.name, ar.title, ar.slug
from (select id, path, split_part(path, '/', 3) as slug_from_path, ip,  method, status, time from log) l, 
	authors a, 
	articles ar
where slug_from_path = ar.slug
and a.id = ar.author;

create unique index log_id_idx on log_view_mat(id);
```
This view joins log entries with articles through the slug and, in doing so, discards log entries not related to articles. The index allows the materialized view to be refreshed concurrently.

```SQL
refresh materialized view concurrently log_view_mat with data;
```
Execute this refresh at least once a day. TODO: add to cron job or to a insert trigger in the log table.

```SQL
create materialized view errors_per_day
as
select t.*, e.errorViews, (100 * e.errorViews)::numeric / t.totalViews as percentage from
(SELECT date_trunc('day', log.time) as day, count(*) as errorViews
FROM log
where status = '404 NOT FOUND'
group by 1
ORDER BY 1) e,
(SELECT date_trunc('day', log.time) as day, count(*) as totalViews
FROM log
group by 1
ORDER BY 1) t
where t.day = e.day
with data;

create unique index day_idx on errors_per_day(day);

refresh materialized view CONCURRENTLY errors_per_day;
```
This view counts the number of views and errors per day to calculate a percentage of errors per day. As with the first, the index allows the view to be updated concurrently.

After creating the views in the database, clone the repository and execute logAnalysis.py:
```bash
git clone https://github.com/albertodepaola/logAnalysis.git log_analysis;
cd log_analysis;
python3 logAnalysis.py;
```
 It should give the same output as the ```sample.txt``` file.

# License
The content of this repository is licensed under a [Creative Commons Attribution License](https://creativecommons.org/licenses/by/3.0/us/)




