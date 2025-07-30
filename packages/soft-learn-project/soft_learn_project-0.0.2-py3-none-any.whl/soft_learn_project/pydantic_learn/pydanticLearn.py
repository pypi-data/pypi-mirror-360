from datetime import datetime
import pydantic
from typing import Annotated, Literal
from annotated_types import Gt
import time
import os
import pydantic_settings


class PydanticLearn():
  def __init__(self):
    """https://realpython.com/python-pydantic/#getting-familiar-with-pydantic
    https://docs.pydantic.dev/latest/
    Pydantic是Python中使用最广泛的数据验证库。
    - Pydantic是一个功能强大的Python库，它利用类型提示帮助您轻松验证和序列化数据模式。这使您的代码更加健壮、易读、简洁，并且更易于调试。Pydantic还与许多流行的静态类型工具和ide集成得很好，这允许您在运行代码之前捕获模式问题。
    - Pydantic定义数据模式的主要方法是通过模型。Pydantic模型是一个对象，类似于Python数据类，用于定义和存储带有注释字段的实体的数据。与数据类不同，Pydantic的重点是自动数据解析、验证和序列化。
    """
    pass

  def install(self):
    """conda install pydantic -c conda-forge
    To install optional dependencies along with Pydantic:
    pip install 'pydantic[email,timezone]'
    """
    pass

  def get_env_var(self,
                  env_file='xxx|None',
                  ):
    """可以设置从文件读取

    Args:
        env_file (str, optional): _description_. Defaults to 'xxx|None'.

    Returns:
        _type_: _description_
    """
    class AppConfig(pydantic_settings.BaseSettings):
      model_config = pydantic_settings.SettingsConfigDict(
          env_file=env_file,
          env_file_encoding="utf-8",
          case_sensitive=False,
          extra="allow",  # "forbid", # 禁止在.env文件中使用额外的环境变量。
      )

      pythonpath: str = pydantic.Field()
      HOMEBREW_BOTTLE_DOMAIN: str
      # database_host: pydantic.HttpUrl
      # database_user: str = pydantic.Field(min_length=5)
      # database_password: str = pydantic.Field(min_length=10)
      # api_key: str = pydantic.Field(min_length=20)

    env_var = AppConfig()
    return env_var

  # 教学: Pydantic是什么？为什么它被如此广泛地采用
  # 如何安装Pydantic
  # 如何解析，验证和序列化数据模式与BaseModel和验证器
  # 如何使用@validate_call为函数编写自定义验证逻辑
  # 如何解析和验证环境变量与pydantic设置
  # Pydantic使您的代码更加健壮和可信，并且它在一定程度上弥补了Python的易用性与静态类型语言的内置数据验证之间的差距。对于您可能拥有的任何数据解析、验证和序列化用例，Pydantic都有一个优雅的解决方案

  def Working_With_Pydantic_BaseModels(self):
    # 假设您正在构建人力资源部门用来管理员工信息的应用程序，并且需要一种方法来验证新员工信息的格式是否正确。例如，每个员工都应该有ID、姓名、电子邮件、出生日期、工资、部门和福利选择。这是Pydantic模型的完美用例！
    # 要定义你的雇员模型，你需要创建一个继承Pydantic的BaseModel的类：
    from datetime import date
    from uuid import UUID, uuid4
    from enum import Enum
    from pydantic import BaseModel, EmailStr

    # 首先，导入定义员工模型所需的依赖项。然后创建一个枚举来表示公司中的不同部门，并使用它来注释员工模型中的部门字段。
    class Department(Enum):
      HR = "HR"
      SALES = "SALES"
      IT = "IT"
      ENGINEERING = "ENGINEERING"

    class Employee(BaseModel):
      employee_id: UUID = uuid4()
      name: str
      email: EmailStr
      date_of_birth: date
      salary: float
      department: Department
      elected_benefits: bool
    # 创建Employee对象的最简单方法是像创建任何其他Python对象一样对其进行实例化。
    Employee(name="Chris DeTuma",
             email="cdetuma@example.com",
             date_of_birth="1998-04-02",
             salary=123_000.00,
             department="IT",
             elected_benefits=True,)
    # 接下来，看看Pydantic在尝试将无效数据传递给Employee实例时是如何响应的：
    Employee(employee_id="123", name=False,
             email="cdetumaexamplecom", date_of_birth="1939804-02",
             salary="high paying", department="PRODUCT", elected_benefits=300,)
    # Pydantic的BaseModel配备了一套方法，可以轻松地从其他对象（如字典和JSON）创建模型。例如，如果你想从字典中实例化一个Employee对象，你可以使用.model_validate（）类方法：
    new_employee_dict = {
        "name": "Chris DeTuma",
        "email": "cdetuma@example.com",
        "date_of_birth": "1998-04-02",
        "salary": 123_000.00,
        "department": "IT",
        "elected_benefits": True, }
    Employee.model_validate(new_employee_dict)
    # You can do the same thing with JSON objects using .model_validate_json():
    new_employee_json = """{"employee_id":"d2e7b773-926b-49df-939a-5e98cbb9c9eb","name":"Eric Slogrenta","email":"eslogrenta@example.com","date_of_birth":"1990-01-02","salary":125000.0,"department":"HR","elected_benefits":false}"""
    new_employee = Employee.model_validate_json(new_employee_json)
    # 你也可以将Pydantic模型序列化为字典和JSON：
    new_employee.model_dump()
    new_employee.model_dump_json()
    # JSON模式告诉您期望哪些字段以及JSON对象中表示哪些值。您可以将其视为Employee类定义的JSON版本。下面是如何为Employee生成JSON模式：
    Employee.model_json_schema()

    # 至此，您现在了解了如何使用Pydantic的BaseModel来验证和序列化数据。接下来，您将学习如何使用字段来进一步定制验证。

  def Using_Fields_for_Customization_and_Metadata(self):
    from datetime import date
    from uuid import UUID, uuid4
    from enum import Enum
    from pydantic import BaseModel, EmailStr, Field

    class Department(Enum):
      HR = "HR"
      SALES = "SALES"
      IT = "IT"
      ENGINEERING = "ENGINEERING"
    # 到目前为止，Employee模型验证了每个字段的数据类型，并确保某些字段（如email、date_of_birth和department）采用有效格式。但是，假设您还希望确保薪水是正数，名称不是空字符串，并且电子邮件包含您公司的域名。您可以使用Pydantic的Field类来完成此操作。
    # Field类允许您自定义并向模型的字段添加元数据。要了解它是如何工作的，请看下面的例子：
    # alias：当您想为字段分配别名时，可以使用此参数。例如，您可以允许date_of_birth被称为birth_date，或者允许salary被称为compensation。您可以在实例化或序列化模型时使用这些别名。
    # repr：这个布尔参数决定一个字段是否显示在模型的字段表示中。在本例中，打印Employee实例时不会看到date_of_birth或salary。

    class Employee(BaseModel):
      employee_id: UUID = Field(default_factory=uuid4, frozen=True)
      name: str = Field(min_length=1, frozen=True)
      email: EmailStr = Field(pattern=r".+@example\.com$")
      date_of_birth: date = Field(alias="birth_date", repr=False, frozen=True)
      salary: float = Field(alias="compensation", gt=0, repr=False)
      department: Department
      elected_benefits: bool

    employee_data = {
        "name": "Clyde Harwell",
        "email": "charwell@example.com",
        "birth_date": "2000-06-12",
        "compensation": 100_000,
        "department": "ENGINEERING",
        "elected_benefits": True,
    }

    employee = Employee.model_validate(employee_data)
    # 现在，您已经牢固地掌握了Pydantic的BaseModel和Field类。仅凭这些，您就可以在数据模式上定义许多不同的验证规则和元数据，但有时这还不够。接下来，您将使用Pydantic验证器进一步进行字段验证。
    return employee

  def Working_With_Validators(self):
    # 到目前为止，您已经使用Pydantic的BaseModel来验证具有预定义类型的模型字段，并且合并了Field来进一步定制验证。虽然仅使用BaseModel和Field就可以完成很多工作，但对于需要自定义逻辑的更复杂的验证场景，您需要使用Pydantic验证器。
    # 使用验证器，您可以执行任何可以在函数中表达的验证逻辑。接下来您将看到如何做到这一点。
    # 继续以员工为例，假设您的公司有一项政策，即他们只雇用年满18岁的员工。任何时候创建一个新的Employee对象，都需要确保该雇员的年龄大于18岁。要处理这个问题，您可以添加一个年龄字段，并使用field类强制员工至少年满18岁。然而，这似乎是多余的，因为您已经存储了员工的出生日期。
    # 更好的解决方案是使用Pydantic字段验证器。字段验证器允许您通过向模型中添加类方法，将自定义验证逻辑应用于BaseModel字段。要强制所有员工至少年满18岁，你可以在Employee模型中添加以下字段验证器：
    from datetime import date
    from uuid import UUID, uuid4
    from enum import Enum
    from pydantic import BaseModel, EmailStr, Field, field_validator
    from datetime import date, timedelta

    class Department(Enum):
      HR = "HR"
      SALES = "SALES"
      IT = "IT"
      ENGINEERING = "ENGINEERING"

    class Employee(pydantic.BaseModel):
      employee_id: UUID = Field(default_factory=uuid4, frozen=True)
      name: str = Field(min_length=1, frozen=True)
      email: EmailStr = Field(pattern=r".+@example\.com$")
      date_of_birth: date = Field(alias="birth_date", repr=False, frozen=True)
      salary: float = Field(alias="compensation", gt=0, repr=False)
      department: Department
      elected_benefits: bool

      @pydantic.field_validator("date_of_birth")
      @classmethod
      def check_valid_age(cls, date_of_birth: date) -> date:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        if date_of_birth > eighteen_years_ago:
          raise ValueError("Employees must be at least 18 years old.")

        return date_of_birth
    # 验证
    young_employee_data = {
        "name": "Jake Bar",
        "email": "jbar@example.com",
        "birth_date": date.today() - timedelta(days=365 * 17),
        "compensation": 90_000,
        "department": "SALES",
        "elected_benefits": True,
    }

    Employee.model_validate(young_employee_data)
    # 可以想象，Pydantic的field_validator（）使您能够任意自定义字段验证。但是，如果您想将多个字段相互比较或将模型作为一个整体进行验证，field_validator（）将不起作用。为此，您需要使用模型验证器。
    # 例如，假设您的公司只雇用IT部门的合同工。因此，IT工作者没有资格获得福利，他们的elected_benefits字段应该为False。你可以使用Pydantic的model_validator（）来强制执行这个约束：

    from typing import Self
    from datetime import date
    from uuid import UUID, uuid4
    from enum import Enum
    from pydantic import (
        BaseModel,
        EmailStr,
        Field,
        field_validator,
        model_validator,
    )

    class Department(Enum):
      HR = "HR"
      SALES = "SALES"
      IT = "IT"
      ENGINEERING = "ENGINEERING"

    class Employee(BaseModel):
      employee_id: UUID = Field(default_factory=uuid4, frozen=True)
      name: str = Field(min_length=1, frozen=True)
      email: EmailStr = Field(pattern=r".+@example\.com$")
      date_of_birth: date = Field(alias="birth_date", repr=False, frozen=True)
      salary: float = Field(alias="compensation", gt=0, repr=False)
      department: Department
      elected_benefits: bool

      @pydantic.field_validator("date_of_birth")
      @classmethod
      def check_valid_age(cls, date_of_birth: date) -> date:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        if date_of_birth > eighteen_years_ago:
          raise ValueError("Employees must be at least 18 years old.")

        return date_of_birth

      # model_validator 模型验证部分
      # 当您在@model_validator中将mode设置为after时，Pydantic会等到您实例化模型之后才运行.check_it_benefits（）。
      @model_validator(mode="after")
      def check_it_benefits(self) -> Self:
        department = self.department
        elected_benefits = self.elected_benefits

        if department == Department.IT and elected_benefits:
          raise ValueError(
              "IT employees are contractors and don't qualify for benefits"
          )
        return self

    pass

  def Using_Validation_Decorators_to_Validate_Functions():
    """
    - 虽然BaseModel是Pydantic用于验证数据模式的基本类，但您也可以使用Pydantic使用@validate_call装饰器来验证函数参数。这允许您创建具有信息类型错误的健壮函数，而无需手动实现验证逻辑。
    - 为了了解这是如何工作的，假设您正在编写一个函数，该函数在客户购买后向客户发送发票。您的函数接受客户的姓名、电子邮件、购买的物品和总账单金额，并构造并向他们发送电子邮件。您需要验证所有这些输入，因为输入错误可能导致电子邮件无法发送、格式错误或客户发票错误。
    """
    import time
    from typing import Annotated
    from pydantic import PositiveFloat, Field, EmailStr, validate_call
    # 首先，导入编写和注释send_invoice（）所需的依赖项。然后创建带有@validate_call装饰的send_invoice（）。在执行send_invoice（）之前，@validate_call确保每个输入都符合您的注释。在这种情况下，@validate_call检查client_name是否至少有一个字符，client_email格式是否正确，items_purchase是一个字符串列表，amount_owned是一个正浮点数。

    @validate_call
    def send_invoice(
        client_name: Annotated[str, Field(min_length=1)],
        client_email: EmailStr,
        items_purchased: list[str],
        amount_owed: PositiveFloat,
    ) -> str:

      email_str = f"""
      Dear {client_name}, \n
      Thank you for choosing xyz inc! You
      owe ${amount_owed:,.2f} for the following items: \n
      {items_purchased}
      """

      print(f"Sending email to {client_email}...")
      time.sleep(2)

      return email_str
    # 无效测试
    email_str = send_invoice(client_name="",
                             client_email="ajolawsonfakedomain.com",
                             items_purchased=["pie", "cookie", 17],
                             amount_owed=0,)
    email_str = send_invoice(client_name="Andrew Jolawson",    client_email="ajolawson@fakedomain.com",
                             items_purchased=["pie", "cookie", "cake"],    amount_owed=20,)
    # 虽然@validate_call不如BaseModel灵活，但您仍然可以使用它对函数参数应用强大的验证。这为您节省了大量时间，并使您避免编写样板类型检查和验证逻辑。如果您以前这样做过，您就会知道为每个函数参数编写断言语句是多么麻烦。对于许多用例，@validate_call会为您解决这个问题。
    pass

  def Managing_Settings(self):
    """
    - 配置Python应用程序最流行的方法之一是使用环境变量。环境变量是一个存在于操作系统中的变量，位于Python代码之外，但可以被代码或其他程序读取。希望存储为环境变量的数据示例包括密钥、数据库凭据、API凭据、服务器地址和访问令牌。
    - 环境变量经常在开发和生产之间发生变化，其中许多包含敏感信息。因此，您需要一种健壮的方法来解析、验证和集成代码中的环境变量。这是pydantic-settings的一个完美用例，这也是您将在本节中探索的内容。
    - pydantic-settings是Python中管理环境变量的最强大的方法之一，它已经被像FastAPI这样的流行库广泛采用和推荐。您可以使用pydani -settings来创建模型，类似于BaseModel，用来解析和验证环境变量。
    - 为了了解这是如何工作的，假设您的应用程序连接到数据库和另一个API服务。您的数据库凭据和API密钥可能会随着时间的推移而更改，并且通常会根据您所部署的环境而更改。为了处理这个问题，你可以创建下面的basessettings模型：

    """

    # 在这个脚本中，您导入创建basessettings模型所需的依赖项。然后定义一个模型AppConfig，它继承自basessettings并存储关于数据库和API键的字段。在本例中，database_host必须是一个有效的HTTP URL，其余字段具有最小长度约束。

    class AppConfig(pydantic_settings.BaseSettings):
      database_host: pydantic.HttpUrl
      database_user: str = pydantic.Field(min_length=5)
      database_password: str = pydantic.Field(min_length=10)
      api_key: str = pydantic.Field(min_length=20)
    # 接下来，打开终端并添加以下环境变量。如果你使用的是Linux、macOS或Windows Bash，你可以使用export命令：
    # $ export DATABASE_HOST = "http://somedatabaseprovider.us-east-2.com"
    # $ export DATABASE_USER = "username"
    # $ export DATABASE_PASSWORD = "asdfjl348ghl@9fhsl4"
    # $ export API_KEY = "ajfsdla48fsdal49fj94jf93-f9dsal"
    # 或者如下
    os.environ['DATABASE_HOST'] = "http://somedatabaseprovider.us-east-2.com"
    os.environ['DATABASE_USER'] = "username"
    os.environ['DATABASE_PASSWORD'] = "asdfjl348ghl@9fhsl4"
    os.environ['API_KEY'] = "ajfsdla48fsdal49fj94jf93-f9dsal"
    # 可以获得环境变量
    # 注意，在实例化AppConfig时没有指定任何字段名。相反，您的basessettings模型将从您设置的环境变量中读取字段。还要注意，您导出了所有大写字母的环境变量，但是AppConfig成功地解析并存储了它们。这是因为basessettings在将环境变量与字段名匹配时不区分大小写。
    AppConfig()
    # AppConfig().api_key
    # 最后，您将学习如何使用SettingsConfigDict进一步自定义basessettings的行为。
    pass

  def Customizing_Settings_With_SettingsConfigDict(self):
    """
    """
    # 在前面的示例中，您看到了如何创建解析和验证环境变量的basessettings模型的基本示例。但是，您可能希望进一步定制BaseSettings模型的行为，您可以使用SettingsConfigDict完成此操作。
    # 假设您不能手动导出每个环境变量（通常是这种情况），您需要从.env文件中读取它们。您需要确保在解析时basessettings区分大小写，并且除了您在模型中指定的环境变量之外，.env文件中没有其他环境变量。下面是如何使用SettingsConfigDict：

    class AppConfig(pydantic_settings.BaseSettings):
      model_config = pydantic_settings.SettingsConfigDict(
          env_file='/Users/wangjinlong/job/soft_learn/py_package_learn/pydantic_learn/example_env.env',  # ".env",
          env_file_encoding="utf-8",
          # case_sensitive=True,
          extra="allow",  # "forbid", # 禁止在.env文件中使用额外的环境变量。
      )

      database_host: pydantic.HttpUrl
      database_user: str = pydantic.Field(min_length=5)
      database_password: str = pydantic.Field(min_length=10)
      api_key: str = pydantic.Field(min_length=20)
      # path: str
    # 解析并验证了.env文件中的环境变量。
    AppConfig()
    pass

  # my example
  def my_journals(self,
                  name='a',
                  website='h',
                  review_cycle=0,
                  partition_中国科学院分区=0,
                  impact_factor=0,
                  ratio_录用比例=0,
                  journal_standered='',
                  ):
    class Journal(pydantic.BaseModel):
      """--- 可以投稿的期刊  **中科院分区** **审稿周期** **影响因子** **网址**
      """
      name: str = pydantic.Field(min_length=1, frozen=True)
      website: str = ''
      review_cycle: float = 0
      partition_中国科学院分区: int = 0
      impact_factor: float = 0
      ratio_录用比例: float | str = 0
      journal_standered: str = ''

    journal_instance = Journal(name=name,
                               website=website,
                               review_cycle=review_cycle,
                               partition_中国科学院分区=partition_中国科学院分区,
                               impact_factor=impact_factor,
                               ratio_录用比例=ratio_录用比例,
                               journal_standered=journal_standered,)
    return journal_instance

  def get_paper_instance(self, cite='wang2017ab',
                         title='Ab initio study of He-He interactions in homogeneous electron gas',
                         author='Wang, Jinlong and Niu, Liang-Liang and Zhang, Ying',
                         journal='Nuclear Instruments and Methods in Physics Research Section B',
                         volume=393,
                         pages='140-143',
                         year=2017,
                         publisher='Elsevier',
                         number=''):
    class Paper(pydantic.BaseModel):
      """cite: 引用时用的信息
      """
      cite: str = 'wang2017ab'
      title: str = 'Ab initio study of He-He interactions in homogeneous electron gas'
      author: str = 'Wang, Jinlong and Niu, Liang-Liang and Zhang, Ying'
      journal: str = 'Nuclear Instruments and Methods in Physics Research Section B: Beam Interactions with Materials and Atoms'
      volume: str | int = 393
      pages: str = '140-143'
      year: int | str = 2017
      publisher: str = 'Elsevier'
      number: str = ''

    paper_instance = Paper(
        cite=cite,
        title=title,
        author=author,
        journal=journal,
        volume=volume,
        pages=pages,
        year=year,
        publisher=publisher,
        number=number)
    return paper_instance

  # --- old

  def Monitor_Pydantic_with_Logfire(self):
    """
    import logfire
    logfire.configure()
    logfire.instrument_pydantic()

    class Delivery(pydantic.BaseModel):
      timestamp: datetime
      dimensions: tuple[int, int]

    # this will record details of a successful validation to logfire
    m = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])
    print(repr(m.timestamp))
    # > datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=TzInfo(UTC))
    print(m.dimensions)
    # > (10, 20)

    Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10'])
    """
    pass

  def example_Pydantic_Successful(self):
    # 为了了解Pydantic的工作原理，让我们从一个简单的例子开始，创建一个继承BaseModel的自定义类：
    class User(pydantic.BaseModel):
      id: int
      name: str = 'John Doe'
      signup_ts: datetime | None
      tastes: dict[str, pydantic.PositiveInt]

    external_data = {
        'id': 123,
        'signup_ts': '2019-06-01 12:22',
        'tastes': {
            'wine': 9,
            b'cheese': 7,
            'cabbage': '1',
        },
    }

    user = User(**external_data)
    print(user.id)
    user.model_dump()

  def example_Pydantic_fail(self):
    # 如果验证失败，Pydantic将引发一个错误，并详细说明出错的地方：
    class User(pydantic.BaseModel):
      id: int
      name: str = 'John Doe'
      signup_ts: datetime | None
      tastes: dict[str, pydantic.PositiveInt]

    external_data = {'id': 'not an int', 'tastes': {}}

    try:
      User(**external_data)
    except pydantic.ValidationError as e:
      print(e.errors())
    pass

  def example_type_hints(self):
    from typing import Annotated, Literal
    from annotated_types import Gt

    class Fruit(pydantic.BaseModel):
      name: str
      color: Literal['red', 'green']
      weight: Annotated[float, Gt(0)]
      bazam: dict[str, list[tuple[int, bool, float]]]

    Fruit(name='Apple',
          color='red',
          weight=4.2,
          bazam={'foobar': [(1, True, 0.1)]},)
    return Fruit

  def example_Serialization_3ways(self):

    class Meeting(pydantic.BaseModel):
      when: datetime
      where: bytes
      why: str = 'No idea'

    m = Meeting(when='2020-01-01T12:00', where='home')
    print(m.model_dump(exclude_unset=True))
    # > {'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}
    print(m.model_dump(exclude={'where'}, mode='json'))
    # > {'when': '2020-01-01T12:00:00', 'why': 'No idea'}
    print(m.model_dump_json(exclude_defaults=True))
    # > {"when":"2020-01-01T12:00:00","where":"home"}
    pass

  def example_JSON_Schema(self):

    class Address(pydantic.BaseModel):
      street: str
      city: str
      zipcode: str

    class Meeting(pydantic.BaseModel):
      when: datetime
      where: Address
      why: str = 'No idea'

    print(Meeting.model_json_schema())

  def example_Strict_mode(self):

    class Meeting(pydantic.BaseModel):
      when: datetime
      where: bytes

    m = Meeting.model_validate({'when': '2020-01-01T12:00', 'where': 'home'})
    print(m)
    # > when=datetime.datetime(2020, 1, 1, 12, 0) where=b'home'
    try:
      m = Meeting.model_validate(
          {'when': '2020-01-01T12:00', 'where': 'home'}, strict=True
      )
    except pydantic.ValidationError as e:
      print(e)
      """
        2 validation errors for Meeting
        when
          Input should be a valid datetime [type=datetime_type, input_value='2020-01-01T12:00', input_type=str]
        where
          Input should be a valid bytes [type=bytes_type, input_value='home', input_type=str]
        """

    m_json = Meeting.model_validate_json(
        '{"when": "2020-01-01T12:00", "where": "home"}'
    )
    m_json

  def example_schema_based_on_TypedDict(self):
    from typing_extensions import NotRequired, TypedDict

    class Meeting(TypedDict):
      when: datetime
      where: bytes
      why: NotRequired[str]

    meeting_adapter = pydantic.TypeAdapter(Meeting)
    m = meeting_adapter.validate_python(
        {'when': '2020-01-01T12:00', 'where': 'home'}
    )
    print(m)
    # > {'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}
    meeting_adapter.dump_python(m, exclude={'where'})
    meeting_adapter.json_schema()

    pass

  def example_wrap_validators(self):
    from typing import Any
    from pydantic_core.core_schema import ValidatorFunctionWrapHandler

    class Meeting(pydantic.BaseModel):
      when: datetime

      @pydantic.field_validator('when', mode='wrap')
      def when_now(
          cls, input_value: Any, handler: ValidatorFunctionWrapHandler
      ) -> datetime:
        if input_value == 'now':
          return datetime.now()
        when = handler(input_value)
        # in this specific application we know tz naive datetimes are in UTC
        if when.tzinfo is None:
          when = when.replace(tzinfo=time.timezone.utc)
        return when

    print(Meeting(when='2020-01-01T12:00+01:00'))
    print(Meeting(when='now'))
    print(Meeting(when='2020-01-01T12:00'))
