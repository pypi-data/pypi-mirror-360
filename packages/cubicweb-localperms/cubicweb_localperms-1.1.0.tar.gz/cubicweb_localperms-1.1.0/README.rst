Summary
-------

This cube allows definition of local permissions using a generic
`CWPermission` entity type which you should use in your schema
definition.

A `CWPermission` entity type:

* has a name and a label

* means groups linked to it through the 'require_group' relation have
  the <name> permission on entities linked through the
  'require_permission' object relation.

To speed-up things, a 'has_group_permission' relation is automatically
maintained, so 'P require_group G, U in_group G' is equivalent to 'U
has_group_permission P'.

Client cubes should explicitly add 'X granted_permission CWPermission'
and 'X require_permission CWPermission' for each type that should have
local permission, the first one being explicitly granted and the other
automatically propagated. Hence possible subjects of
`granted_permission` should be a subset of `require_permission`
possible subjects.

You should then use `require_permission` in your schema security
definition, since this is the one which is automatically propagated.

Example of configuration
------------------------

.. sourcecode:: python

  class granted_permission(RelationDefinition):
      subject = 'Project'
      object = 'CWPermission'

  class require_permission(RelationDefinition):
      subject = ('Project', 'Version')
      object = 'CWPermission'

  class Project(EntityType):
      """a project, only visible to managers and users having the 'view' local permission
      """
      __permissions__ = {
         'read':   ('managers', ERQLExpression('X require_permission P, P name "view", '
                                               'U has_group_permission P'),),
         'update': ('managers', 'owners',),
         'delete': ('managers', ),
         'add':    ('managers', 'users',),)
         }

  class Version(EntityType):
      """a version defines the content of a particular project's release"""
      __permissions__ = {
         'read':   ('managers', ERQLExpression('X require_permission P, P name "view", '
                                               'U has_group_permission P'),),
         'update': ('managers', 'owners',),
         'delete': ('managers', ),
         'add':    ('managers', 'users',),)
         }

  class version_of(RelationDefinition):
      """link a version to its project. A version is necessarily linked to one and
      only one project.
      """
      __permissions__ = {
         'read':   ('managers', 'users',),
         'delete': ('managers', ),
         'add':    ('managers', RRQLExpression('O require_permission P, P name "manage",'
                                               'U has_group_permission P'),)
                     }
      subject = 'Version'
      object = 'Project'
      cardinality = '1*'


This configuration indicates that we've two distinct permissions
(forthcoming `CWPermission` entities):

* one named 'view', which allows some users to view a particular
  project and its versions

* another named "manage" which provides rights to create new versions
  on a project

.. Note::

  Notice that we granted 'add' permission of `Version` to the 'users'
  group.  The idea is that it's hard for the web ui to get 'add'
  permission until the entity doesn't exist yet.  So we let the
  'version_of' relation carry the security (easier to check, since we
  usually know the project on which we may want to add a version). And
  as we know that this relation is mandatory for `Version`, we also
  ensure users can only add versions on project where they have the
  "manage" permission.

  Also, we let the 'read' permission on 'version_of' not only because
  rql expression aren't supported there, but because in this case
  we know one won't be able to see a relation between two entities he
  can't see...


Now the idea is that managers will grant permission on projects, and
those will then be propagated as configured. You will want to use sets in
`cubicweb_localperms.hooks` to configure how permissions should be
propagated when desired. In our example, put in your cube's `hooks.py`
something like:

.. sourcecode:: python

  from cubicweb_localperms import hooks
  # relations where the "main" entity is the object. We could also
  # have modified hooks.S_RELS for relations where the "main" entity
  # is the subject
  hooks.O_RELS.add('version_of')


The permission given to a project will be automatically added/removed as
version are created / deleted.


Last but not least, when defining the entity class for `Project`,
defines `__permissions__` as below:

.. sourcecode:: python

     class Project(AnyEntity):
         __permissions__ = ('view', 'manage',)

So that when going on the 'security' view for a project (in 'more
actions' sub-menu by default), you should be proposed an interface to
configurate local permissions with a combo-box prefilled with proper
permission names instead of a free text input, which greatly reduces the
risk of error.

Also, you'll find in `cubicweb_localperms` some functions to ease building
of rql expression in your schema definition. Those written in above example
could be written as below using those functions:


.. sourcecode:: python

  from cubicweb_localperms import xexpr, oexpr

  class Project(EntityType):
      __permissions__ = {'read':   ('managers', xexpr('view'),),
                         'update': ('managers', 'owners',),
                         'delete': ('managers', ),
                         'add':    ('managers', 'users',),)
                         }

  class Version(EntityType):
      __permissions__ = {'read':   ('managers', xexpr('view'),),
                         'update': ('managers', 'owners',),
                         'delete': ('managers', ),
                         'add':    ('managers', 'users',),)
                         }

  class version_of(RelationDefinition):
      __permissions__ = {'read':   ('managers', 'users',),
                         'update': ('managers', 'owners',),
                         'delete': ('managers', ),
                         'add':    ('managers', oexpr('manage'),)
                        }
