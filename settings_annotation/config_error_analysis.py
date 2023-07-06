"""
add or remove categories for error analysis. After your changes, run  `python manage.py makemigrations` and `python manage.py migrate`
categories currently based on Heineman, D., Dou, Y., Maddela, M., & Xu, W. (2023). Dancing Between Success and Failure: Edit-level Simplification Evaluation using SALSA. arXiv preprint arXiv:2305.14458.
"""


error_analysis_dict = {"conceptual": {
							"bad_deletion": [],
							"coreference": [],
							"repetition": [],
							"contradiction": [],
							"factual_error": [],
							"irrelevant": [],
							},
					   "syntax": {
						   "bad_reorder": [],
						   "bad_structure": [],
						   "bad_split": [],
					   		},
					   "lexical": {
						   "complex_wording": [],
						   "information_rewrite": [],
						   "grammar": [],
					   		},
						"other" : {
							"no_errors": [],
							"unclear": [],
						}
				   }



keys_list_error_operation = sorted([list(trans.keys()) for level, trans in error_analysis_dict.items()])
list_choices_error_operation = sorted(list(set([item for sublist in keys_list_error_operation for item in sublist])))
values_list_error_suboperation = sorted([list(error_analysis_dict[trans].values()) for trans in error_analysis_dict.keys()])
nested_list_choices_error_suboperation = sorted([item for sublist in values_list_error_suboperation for item in sublist])
list_choices_error_suboperation = sorted(list(set([item for sublist in nested_list_choices_error_suboperation for item in sublist])))
tuple_list_choices_error_operation = [(trans, trans) for trans in list_choices_error_operation]
tuple_list_choices_error_suboperation = [(subtrans, subtrans) for subtrans in list_choices_error_suboperation]
tuple_list_error_operation_level = [(item, item) for item in error_analysis_dict.keys()]

error_operation_list = list()
for error_operation_level in sorted(error_analysis_dict.keys()):
	error_operation_list.append(error_operation_level+"#")
	for transformation in sorted(error_analysis_dict[error_operation_level]):
		error_operation_list.append(error_operation_level+"#"+transformation+"*")
		for sub_transformation in sorted(error_analysis_dict[error_operation_level][transformation]):
			error_operation_list.append(error_operation_level+"#"+transformation+"*"+sub_transformation+"+")
