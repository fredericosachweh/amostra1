

drop table device_streamplayer ;
drop table device_streamrecorder ;
drop table device_storage ;
delete from auth_permission where content_type_id IN (SELECT id from django_content_type where app_label = 'device' AND model IN ('storage', 'streamrecorder', 'streamplayer'));
delete from django_admin_log where content_type_id IN (SELECT id from django_content_type where app_label = 'device' AND model IN ('storage', 'streamrecorder', 'streamplayer'));
delete from django_content_type where app_label = 'device' AND model IN ('storage', 'streamrecorder', 'streamplayer');


