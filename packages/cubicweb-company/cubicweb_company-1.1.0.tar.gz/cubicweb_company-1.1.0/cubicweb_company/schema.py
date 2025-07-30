# template's specific schema
from yams.buildobjs import EntityType, SubjectRelation, String


class Company(EntityType):
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)
    web = String(fulltextindexed=True, maxsize=128)
    rncs = String(fulltextindexed=True, maxsize=32)

    headquarters = SubjectRelation('PostalAddress', cardinality='*?', composite='subject')
    phone = SubjectRelation('PhoneNumber', cardinality='*?', composite='subject')
    use_email = SubjectRelation('EmailAddress', cardinality='*?', composite='subject')
    subsidiary_of = SubjectRelation('Company', cardinality='?*')
