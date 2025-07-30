import ast
from typing import Any


SYMBOL = "*"

LABEL_TYPE_ERROR = (
   "'label' must be a string, or a list/tuple containing only strings."
)

class InvalidArgumentError(ValueError): 
    pass


class NoArgumentsError(Exception): 
    pass


class UnDefinedArgument(Exception): 
    pass


class _ExitEarly(Exception): 
    pass


def _check_label_type(label: Any) -> None:
   if not isinstance(label, str):
      raise InvalidArgumentError("Label must be a string.")


def _compare_value_counts(
      total_values: tuple[Any], needed_indices_count: int,
) -> None:
   # Note: `len(total_values)` is always one more than the max index.
   if len(total_values) <= needed_indices_count:
      raise ValueError(
         f"Please set the value to change at position {needed_indices_count}."
      )
    

def _count_symbol(label: str) -> int:
   if not isinstance(label, str):
      raise InvalidArgumentError("`label` must be a string.")
   
   count = 0

   # count only prefix symbols
   for symbol in label:
      if symbol == SYMBOL:
         count += 1
         continue
      return count


def _handle_arg_types(
      label: Any, value: Any | None, index: int=None, get_type: bool=False,
      ) -> dict[str, Any] | tuple[dict[str, Any], ast.AST]:
   if index is not None and not isinstance(index, int):
      raise InvalidArgumentError(
         "The `index` keyword must be a literal value."
      )
      
   if isinstance(label, str):    
      if label == "":
         raise InvalidArgumentError("Label cannot be empty or blank.")  
      elif isinstance(value, (list, tuple)):               
        if len(value) != 0:
          if get_type:
             return ({label: value}, ast.List) # use ast.List for both list and tuple (same handling). 
          
          return {label: value}    
            
        raise InvalidArgumentError("The contents are empty.")
      
      elif isinstance(value, dict):
         raise InvalidArgumentError(
            "dict is not supported for 'value'."
         )     
      else:
         if get_type:
            return ({label: value}, ast.Name) # use ast.Name for both Name and Attribute (same handling).
         
         return {label: value}
      
   elif isinstance(label, dict):      
      if len(label) == 0:
         raise InvalidArgumentError("The contents are empty.")   
      elif value is None:
         if get_type:
            return (label, ast.Dict)
         
         return label
      
      raise InvalidArgumentError("If a dict is given, set the values in it.")
   
   else:
      raise InvalidArgumentError("Unsupported argument type.")
