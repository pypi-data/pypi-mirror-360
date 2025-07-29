# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Accretive modules.

    Provides a module type that enforces attribute immutability after
    assignment. This helps ensure that module-level constants remain constant
    and that module interfaces remain stable during runtime.

    The module implementation is derived from :py:class:`types.ModuleType` and
    adds accretive behavior. This makes it particularly useful for:

    * Ensuring constants remain constant
    * Preventing accidental modification of module interfaces

    Also provides a convenience function:

    * ``reclassify_modules``: Converts existing modules to accretive modules.
'''


from . import __
from . import iclasses as _iclasses


ModuleNamespaceDictionary: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, __.typx.Any ] )

DynadocIntrospectionArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.ddoc.IntrospectionControl ],
    __.ddoc.Doc(
        ''' Dynadoc introspection control.

            Which kinds of object to recursively introspect?
            Scan unnannotated attributes?
            Consider base classes?
            Etc...
        ''' ),
]
FinalizeModuleDynadocTableArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.cabc.Mapping[ str, str ] ],
    __.ddoc.Doc( ''' Table of documentation fragments. ''' ),
]
ModuleArgument: __.typx.TypeAlias = __.typx.Annotated[
    str | __.types.ModuleType, __.ddoc.Doc( ''' Module or module name. ''' ),
]
ModuleNamespaceArgument: __.typx.TypeAlias = __.typx.Annotated[
    str | __.types.ModuleType | ModuleNamespaceDictionary,
    __.ddoc.Doc( ''' Module, module name, or module namespace. ''' ),
]
RecursiveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.ddoc.Doc( ''' Recursively reclassify package modules? ''' )
]
ReplacementClassArgument: __.typx.TypeAlias = __.typx.Annotated[
    type[ __.types.ModuleType ],
    __.ddoc.Doc( ''' New class for module. ''' ),
]


class Module(
    __.types.ModuleType,
    metaclass = _iclasses.Class,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Accretive module. '''

    _dynadoc_fragments_ = ( 'module', 'module conceal', 'module accrete' )


def finalize_module( # noqa: PLR0913
    module: ModuleArgument, /,
    *fragments: __.ddoc.interfaces.Fragment,
    attributes_namer: __.AttributesNamer = __.calculate_attrname,
    dynadoc_introspection: DynadocIntrospectionArgument = __.absent,
    dynadoc_table: FinalizeModuleDynadocTableArgument = __.absent,
    recursive: RecursiveArgument = False,
    replacement_class: ReplacementClassArgument = Module,
) -> None:
    ''' Combines Dynadoc docstring assignment and module reclassification.

        Applies module docstring generation via Dynadoc introspection,
        then reclassifies modules for accretion and concealment.

        When recursive is False, automatically excludes module targets from
        dynadoc introspection to document only the provided module. When
        recursive is True, automatically includes module targets so Dynadoc
        can recursively document all modules.
    '''
    nomargs: dict[ str, __.typx.Any ] = dict(
        attributes_namer = attributes_namer,
        recursive = recursive,
        replacement_class = replacement_class )
    if not __.is_absent( dynadoc_introspection ):
        nomargs[ 'dynadoc_introspection' ] = dynadoc_introspection
    if not __.is_absent( dynadoc_table ):
        nomargs[ 'dynadoc_table' ] = dynadoc_table
    __.ccstd.finalize_module( module, *fragments, **nomargs )


@__.typx.deprecated( "Use 'finalize_module' function instead." )
def reclassify_modules(
    module: ModuleNamespaceArgument, /, *,
    recursive: RecursiveArgument = False,
) -> None:
    ''' Reclassifies modules to be accretive.

        Can operate on individual modules or entire package hierarchies.

        Only converts modules within the same package to prevent unintended
        modifications to external modules.

        When used with a dictionary, converts any module objects found as
        values if they belong to the same package.

        Has no effect on already-accretive modules.
    '''
    __.ccstd.reclassify_modules(
        module,
        attributes_namer = __.calculate_attrname,
        replacement_class = Module )
