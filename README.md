
create or replace materialized view log_view_mat as
select l.*, a.name, ar.title, ar.slug
from (select id, path, split_part(path, '/', 3) as slug_from_path, ip,  method, status, time from log) l, 
	authors a, 
	articles ar
where slug_from_path = ar.slug
and a.id = ar.author;

create unique index log_id_idx on log_view_mat(id);

refresh materialized view concurrently log_view_mat with data;

select count(*) as views, slug
from log_view
where slug != ''
and status = '200 OK'
group by slug
order by views desc;

select count(*) as views, slug, name, title
from log_view
where slug != ''
and status = '200 OK'
group by slug, name, title
order by views desc;


SELECT date_trunc('day', log.time) "day", count(*) as totalViews
FROM log
group by 1
ORDER BY 1;

SELECT date_trunc('day', log.time) "day", count(*) as errorViews
FROM log
where status = '404 NOT FOUND'
group by 1
ORDER BY 1;

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
order by percentage desc;


c.execute("select t.*, e.errorViews, (100 * e.errorViews)::numeric / t.totalViews as percentage from " +
              "(SELECT date_trunc('day', log.time) as day, count(*) as errorViews " +
              "FROM log " +
              "where status = '404 NOT FOUND' " +
              "group by 1 " +
              "ORDER BY 1) e, " +
              "(SELECT date_trunc('day', log.time) as day, count(*) as totalViews " +
              "FROM log " +
              "group by 1 " +
              "ORDER BY 1) t " +
              "where t.day = e.day " +
              #"and percentage > %s " +
              "order by percentage desc;", (percent_error_threshold,))



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


select * from
errors_per_day
where percentage > 0.7
order by percentage desc;

