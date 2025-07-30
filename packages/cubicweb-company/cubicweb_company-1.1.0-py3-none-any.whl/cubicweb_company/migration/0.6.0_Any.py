# db cleanup, some data has been found in an internal instance which is not
# anymore allowed by the schema
sql("DELETE FROM is_part_of_relation USING entities WHERE eid_from=eid and type='Company'")
# use sql queries to turn division into company without much effort
sql("INSERT INTO cw_Company (cw_eid,cw_name,cw_web,cw_creation_date,cw_modification_date,cw_cwuri) "
    "SELECT cw_eid,cw_name,cw_web,cw_creation_date,cw_modification_date,cw_cwuri FROM cw_Division")
sql("UPDATE entities SET type='Company' WHERE type='Division'")
sql('INSERT INTO subsidiary_of_relation(eid_from, eid_to) SELECT eid_from, eid_to FROM is_part_of_relation')
sql('DELETE FROM cw_Division')

# though this is easier using rql
rql('SET X is Y WHERE X is Division, Y name "Company"')
rql('SET X is_instance_of Y WHERE X is_instance_of Division, Y name "Company"')
# we're done, this should simply cleanup the schema without loosing any content
drop_entity_type('Division')
drop_relation_type('is_part_of')
