import warnings


class MyDeprecatedClass:

  def __init__(self):
    """示例：类弃用警告
    """
    warnings.warn(
        "MyDeprecatedClass is deprecated and will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    # 类的初始化逻辑
    print("Initializing MyDeprecatedClass")

  def my_deprecated_method(self):
    """示例：方法弃用警告
    """

    warnings.warn(
        "my_deprecated_method is deprecated and will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    # 方法的逻辑
    print("Calling my_deprecated_method")


class Features():
  def __init__(self) -> None:
    pass

  def deprecated_warning(self,):
    """示例：方法弃用警告
    """
    # from py_package_learn.inspect_learn import inspectLearn
    # current_function_name = inspectLearn.Features().log_function_name()
    # warnings.warn(
    #     f"{current_function_name} is deprecated and will be removed in a future version. "+warn_extra_str,
    #     DeprecationWarning,
    #     stacklevel=2)
    # 或者
    # warnings.warn('考虑弃用', DeprecationWarning, stacklevel=2)
    # 或者
    warnings.warn('考虑弃用.', stacklevel=2)
