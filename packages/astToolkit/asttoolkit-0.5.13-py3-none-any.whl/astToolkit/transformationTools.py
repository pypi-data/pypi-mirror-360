"""
AST Transformation Tools for Code Optimization and Generation.

(AI generated docstring)

This module provides higher-level transformation tools that operate on AST structures to perform complex code optimizations and
transformations. The module includes five key functions:

1. makeDictionaryFunctionDef: Creates a lookup dictionary mapping function names to their AST definitions within a module,
	enabling efficient access to specific function definitions.

2. inlineFunctionDef: Performs function inlining by recursively substituting function calls with their implementation bodies,
	creating self-contained functions without external dependencies.

3. removeUnusedParameters: Optimizes function signatures by analyzing and removing unused parameters, updating the function
	signature, return statements, and type annotations accordingly.

4. unparseFindReplace: Recursively replaces AST nodes throughout a tree structure using textual representation matching, providing
	a brute-force but effective approach for complex replacements.

5. write_astModule: Converts an IngredientsModule to optimized Python source code and writes it to a file, handling import
	organization and code formatting in the process.

These transformation tools form the backbone of the code optimization pipeline, enabling sophisticated code transformations while
maintaining semantic integrity and performance characteristics.
"""

from astToolkit import (
	Be, DOT, Grab, IfThis, IngredientsFunction, IngredientsModule, Make, NodeChanger, NodeTourist, Then, 木,
)
from autoflake import fix_code as autoflake_fix_code
from collections.abc import Mapping
from copy import deepcopy
from os import PathLike
from pathlib import PurePath
from typing import Any
from Z0Z_tools import raiseIfNone, writeStringToHere
import ast

def makeDictionaryAsyncFunctionDef(astAST: ast.AST) -> dict[str, ast.AsyncFunctionDef]:
	"""
	Make a dictionary of `async def` (***async***hronous ***def***inition) function `name` to `ast.AsyncFunctionDef` (***Async***hronous Function ***Def***inition) `object`.

	This function finds all `ast.AsyncFunctionDef` in `astAST` (Abstract Syntax Tree) and makes a
	dictionary of identifiers as strings paired with `ast.AsyncFunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.AsyncFunctionDef.name` as a string and `ast.AsyncFunctionDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2AsyncFunctionDef : dict[str, ast.AsyncFunctionDef]
		A dictionary of identifier to `ast.AsyncFunctionDef`.
	"""
	dictionaryIdentifier2AsyncFunctionDef: dict[str, ast.AsyncFunctionDef] = {}
	NodeTourist(Be.AsyncFunctionDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2AsyncFunctionDef)).visit(astAST)
	return dictionaryIdentifier2AsyncFunctionDef

def makeDictionaryClassDef(astAST: ast.AST) -> dict[str, ast.ClassDef]:
	"""
	Make a dictionary of `class` definition `name` to `ast.ClassDef` (***Class*** ***Def***inition) `object`.

	This function finds all `ast.ClassDef` in `astAST` (Abstract Syntax Tree) and makes a dictionary
	of identifiers as strings paired with `ast.ClassDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.ClassDef.name` as a string and `ast.ClassDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2ClassDef : dict[str, ast.ClassDef]
		A dictionary of identifier to `ast.ClassDef`.
	"""
	dictionaryIdentifier2ClassDef: dict[str, ast.ClassDef] = {}
	NodeTourist(Be.ClassDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2ClassDef)).visit(astAST)
	return dictionaryIdentifier2ClassDef

def makeDictionaryFunctionDef(astAST: ast.AST) -> dict[str, ast.FunctionDef]:
	"""
	Make a dictionary of `def` (***def***inition) function `name` to `ast.FunctionDef` (Function ***Def***inition) `object`.

	This function finds all `ast.FunctionDef` in `astAST` (Abstract Syntax Tree) and makes a
	dictionary of identifiers as strings paired with `ast.FunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.FunctionDef.name` as a string and `ast.FunctionDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2FunctionDef : dict[str, ast.FunctionDef]
		A dictionary of identifier to `ast.FunctionDef`.
	"""
	dictionaryIdentifier2FunctionDef: dict[str, ast.FunctionDef] = {}
	NodeTourist(Be.FunctionDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2FunctionDef)).visit(astAST)
	return dictionaryIdentifier2FunctionDef

def makeDictionaryMosDef(astAST: ast.AST) -> dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef]:
	"""
	Make a dictionary of identifier to `ast.AsyncFunctionDef` (***Async***hronous Function ***Def***inition), `ast.ClassDef` (***Class*** ***Def***inition), or `ast.FunctionDef` (Function ***Def***inition) `object`.

	This function finds all `ast.AsyncFunctionDef`, `ast.ClassDef`, and `ast.FunctionDef` in
	`astAST` (Abstract Syntax Tree) and makes a dictionary of identifiers as strings paired with
	`ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of identifiers and
		`ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.

	Returns
	-------
	dictionaryIdentifier2MosDef : dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef]
		A dictionary of identifier to `ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.
	"""
	dictionaryIdentifier2MosDef: dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef] = {}
	dictionaryIdentifier2MosDef.update(makeDictionaryAsyncFunctionDef(astAST))
	dictionaryIdentifier2MosDef.update(makeDictionaryClassDef(astAST))
	dictionaryIdentifier2MosDef.update(makeDictionaryFunctionDef(astAST))
	return dictionaryIdentifier2MosDef

def inlineFunctionDef(identifierToInline: str, module: ast.Module) -> ast.FunctionDef:  # noqa: C901, PLR0912
	"""
	Inline function calls within a function definition to create a self-contained function.

	(AI generated docstring)

	This function takes a function identifier and a module, finds the function definition,
	and then recursively inlines all function calls within that function with their
	implementation bodies. This produces a fully inlined function that doesn't depend
	on other function definitions from the module.

	Parameters
	----------
	identifierToInline : str
		The name of the function to inline.
	module : ast.Module
		The AST module containing the function and its dependencies.

	Returns
	-------
	FunctionDefToInline : ast.FunctionDef
		The inlined function definition as an `ast.FunctionDef` object.

	Raises
	------
		ValueError: If the function to inline is not found in the module.
	"""
	dictionaryFunctionDef: dict[str, ast.FunctionDef] = makeDictionaryFunctionDef(module)
	try:
		FunctionDefToInline = dictionaryFunctionDef[identifierToInline]
	except KeyError as ERRORmessage:
		message = f"FunctionDefToInline not found in dictionaryIdentifier2FunctionDef: {identifierToInline = }"
		raise ValueError(message) from ERRORmessage

	listIdentifiersCalledFunctions: list[str] = []
	findIdentifiersToInline = NodeTourist[ast.Call, ast.expr](IfThis.isCallToName
		, Grab.funcAttribute(Grab.idAttribute(Then.appendTo(listIdentifiersCalledFunctions))))
	findIdentifiersToInline.visit(FunctionDefToInline)

	dictionary4Inlining: dict[str, ast.FunctionDef] = {}
	for identifier in sorted(set(listIdentifiersCalledFunctions).intersection(dictionaryFunctionDef.keys())):
		if NodeTourist(IfThis.matchesMeButNotAnyDescendant(IfThis.isCallIdentifier(identifier)), Then.extractIt).captureLastMatch(module) is not None:
			dictionary4Inlining[identifier] = dictionaryFunctionDef[identifier]

	keepGoing = True
	while keepGoing:
		keepGoing = False
		listIdentifiersCalledFunctions.clear()
		findIdentifiersToInline.visit(Make.Module(list(dictionary4Inlining.values())))

		listIdentifiersCalledFunctions = sorted((set(listIdentifiersCalledFunctions).difference(dictionary4Inlining.keys())).intersection(dictionaryFunctionDef.keys()))
		if len(listIdentifiersCalledFunctions) > 0:
			keepGoing = True
			for identifier in listIdentifiersCalledFunctions:
				if NodeTourist(IfThis.matchesMeButNotAnyDescendant(IfThis.isCallIdentifier(identifier)), Then.extractIt).captureLastMatch(module) is not None:
					FunctionDefTarget = dictionaryFunctionDef[identifier]
					if len(FunctionDefTarget.body) == 1:
						replacement = NodeTourist(Be.Return, Then.extractIt(DOT.value)).captureLastMatch(FunctionDefTarget)
						inliner = NodeChanger[ast.Call, ast.expr | None](
							findThis = IfThis.isCallIdentifier(identifier), doThat = Then.replaceWith(replacement))
						for astFunctionDef in dictionary4Inlining.values():
							inliner.visit(astFunctionDef)
					else:
						inliner = NodeChanger(Be.Assign.valueIs(IfThis.isCallIdentifier(identifier)), Then.replaceWith(FunctionDefTarget.body[0:-1]))
						for astFunctionDef in dictionary4Inlining.values():
							inliner.visit(astFunctionDef)

	for identifier, FunctionDefTarget in dictionary4Inlining.items():
		if len(FunctionDefTarget.body) == 1:
			replacement = NodeTourist(Be.Return, Then.extractIt(DOT.value)).captureLastMatch(FunctionDefTarget)
			inliner = NodeChanger(IfThis.isCallIdentifier(identifier), Then.replaceWith(replacement))
			inliner.visit(FunctionDefToInline)
		else:
			inliner = NodeChanger(Be.Assign.valueIs(IfThis.isCallIdentifier(identifier)), Then.replaceWith(FunctionDefTarget.body[0:-1]))
			inliner.visit(FunctionDefToInline)
	ast.fix_missing_locations(FunctionDefToInline)
	return FunctionDefToInline

def removeUnusedParameters(ingredientsFunction: IngredientsFunction) -> IngredientsFunction:
	"""
	Remove unused parameters from a function's AST definition, return statement, and annotation.

	(AI generated docstring)

	This function analyzes the Abstract Syntax Tree (AST) of a given function and removes
	any parameters that are not referenced within the function body. It updates the
	function signature, the return statement (if it's a tuple containing unused variables),
	and the return type annotation accordingly.

	Parameters
	----------
	ingredientsFunction : IngredientsFunction
		An object containing the AST representation of a function to be processed.

	Returns
	-------
	IngredientsFunction : IngredientsFunction
		The modified IngredientsFunction object with unused parameters and corresponding return
		elements/annotations removed from its AST.
	"""
	list_argCuzMyBrainRefusesToThink = ingredientsFunction.astFunctionDef.args.args + ingredientsFunction.astFunctionDef.args.posonlyargs + ingredientsFunction.astFunctionDef.args.kwonlyargs
	list_arg_arg: list[str] = [ast_arg.arg for ast_arg in list_argCuzMyBrainRefusesToThink]
	listName: list[ast.Name] = []
	fauxFunctionDef = deepcopy(ingredientsFunction.astFunctionDef)
	NodeChanger(Be.Return, Then.removeIt).visit(fauxFunctionDef)
	NodeTourist(Be.Name, Then.appendTo(listName)).visit(fauxFunctionDef)
	listIdentifiers: list[str] = [astName.id for astName in listName]
	listIdentifiersNotUsed: list[str] = list(set(list_arg_arg) - set(listIdentifiers))
	for argIdentifier in listIdentifiersNotUsed:
		remove_arg = NodeChanger(IfThis.is_argIdentifier(argIdentifier), Then.removeIt)
		remove_arg.visit(ingredientsFunction.astFunctionDef)

	list_argCuzMyBrainRefusesToThink = ingredientsFunction.astFunctionDef.args.args + ingredientsFunction.astFunctionDef.args.posonlyargs + ingredientsFunction.astFunctionDef.args.kwonlyargs

	listName = [Make.Name(ast_arg.arg) for ast_arg in list_argCuzMyBrainRefusesToThink]
	replaceReturn = NodeChanger(Be.Return, Then.replaceWith(Make.Return(Make.Tuple(listName))))
	replaceReturn.visit(ingredientsFunction.astFunctionDef)

	list_annotation: list[ast.expr] = [ast_arg.annotation for ast_arg in list_argCuzMyBrainRefusesToThink if ast_arg.annotation is not None]
	ingredientsFunction.astFunctionDef.returns = Make.Subscript(Make.Name('tuple'), Make.Tuple(list_annotation))

	ast.fix_missing_locations(ingredientsFunction.astFunctionDef)

	return ingredientsFunction

def unparseFindReplace(astTree: 木, mappingFindReplaceNodes: Mapping[ast.AST, ast.AST]) -> 木:
	"""
	Recursively replace AST (Abstract Syntax Tree) nodes based on a mapping of find-replace pairs.

	(AI generated docstring)

	This function applies brute-force node replacement throughout an AST tree
	by comparing textual representations of nodes. While not the most semantic
	approach, it provides a reliable way to replace complex nested structures
	when more precise targeting methods are difficult to implement.

	The function continues replacing nodes until no more changes are detected
	in the AST's textual representation, ensuring complete replacement throughout
	the tree structure.

	Parameters
	----------
	astTree : ast.AST
		(abstract syntax tree) The AST structure to modify.
	mappingFindReplaceNodes : Mapping[ast.AST, ast.AST]
		A mapping from source nodes to replacement nodes.

	Returns
	-------
	newTree : ast.AST
		The modified AST structure with all matching nodes replaced.
	"""
	keepGoing = True
	newTree = deepcopy(astTree)

	while keepGoing:
		for nodeFind, nodeReplace in mappingFindReplaceNodes.items():
			NodeChanger(IfThis.unparseIs(nodeFind), Then.replaceWith(nodeReplace)).visit(newTree)

		if ast.unparse(newTree) == ast.unparse(astTree):
			keepGoing = False
		else:
			astTree = deepcopy(newTree)
	return newTree

def write_astModule(ingredients: IngredientsModule, pathFilename: PathLike[Any] | PurePath, packageName: str | None = None) -> None:
	"""
	Convert an IngredientsModule to Python source code and write it to a file.

	(AI generated docstring)

	This function renders an IngredientsModule into executable Python code,
	applies code quality improvements like import organization via autoflake,
	and writes the result to the specified file path.

	The function performs several key steps:
	1. Converts the AST module structure to a valid Python AST
	2. Fixes location attributes in the AST for proper formatting
	3. Converts the AST to Python source code
	4. Optimizes imports using autoflake
	5. Writes the final source code to the specified file location

	This is typically the final step in the code generation assembly line,
	producing optimized Python modules ready for execution.

	Parameters
	----------
	ingredients : IngredientsModule
		The IngredientsModule containing the module definition.
	pathFilename : PathLike[Any] | PurePath
		The file path where the module should be written.
	packageName : str | None = None
		Optional package name to preserve in import optimization.
	"""
	astModule = Make.Module(ingredients.body, ingredients.type_ignores)
	ast.fix_missing_locations(astModule)
	pythonSource: str = raiseIfNone(ast.unparse(astModule))
	autoflake_additional_imports: list[str] = ingredients.imports.exportListModuleIdentifiers()
	if packageName:
		autoflake_additional_imports.append(packageName)
	pythonSource = autoflake_fix_code(pythonSource, autoflake_additional_imports, expand_star_imports=False, remove_all_unused_imports=True, remove_duplicate_keys = False, remove_unused_variables = False)
	writeStringToHere(pythonSource, pathFilename)
