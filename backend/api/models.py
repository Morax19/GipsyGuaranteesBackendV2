from django.db import models
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

"""
    This code defines the models for Gipsy Guarantees Backend
"""
class CustomUserManager(BaseUserManager):
    """
    Custom manager to handle the different users creation
    """
    def create_customer(
        self,
        firstName,
        lastName,
        email,
        password,
        address=None,
        phone=None,
        zip_code=None):
        """
        This method handles the registration for Warranty.Customer and also creates
        the respective User associated with the Warranty.Customer.
        It requires the first name, last name, email, and password.
        The address, phone, and zip code are optional.
        Raises ValueError if the email is not provided.
        :param firstName: First name of the customer
        :param lastName: Last name of the customer
        :param email: Email address of the customer (used as username in User)
        :param password: Password for the user
        :param address: Address of the customer (optional)
        :param phone: Phone number of the customer (optional)
        :param zip_code: Zip code of the customer (optional)
        :return: The created user instance
        """
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Correo electrónico inválido.')

        with transaction.atomic():

            customer = WarrantyCustomer.objects.create(
                FirstName=firstName,
                LastName=lastName,
                EmailAddress=email,
                PhoneNumber=phone,
                Zip=zip_code
            )

            role = Role.get_or_create_role('Cliente')

            user = self.model(
                User=email,
                registrationDate=timezone.now(),
                CustomerID=customer,
                roleID=role,
                is_staff=False
            )

            user.set_password(password)
            user.save(using=self._db)

        return user  
    
    def create_tech(
        self,
        username,
        password,
        regDate,
        roleDescription='Servicio Técnico'):
        """
        This method creates a technical user with the specified username, password,
        registration date, and role description. It requires the username, password,
        and registration date. The role description defaults to 'Servicio Técnico'.
        Raises ValueError if the username is not provided.
        :param username: Username for the technical user (should be an email for consistency)
        :param password: Password for the technical user
        :param regDate: Registration date for the technical user
        :param roleDescription: Description of the role (default is 'Servicio Técnico')
        :return: The created technical user instance
        """
        if not username:
            raise ValueError('El nombre de usuario es obligatorio.')
        
        role = Role.get_or_create_role(roleDescription)

        tech_user = self.model(
            User=username,
            registrationDate=regDate,
            roleID=role,
            is_staff=True
        )

        tech_user.set_password(password)
        tech_user.save(using=self._db)

        return tech_user

    def create_admin(
        self,
        username,
        password,
        regDate,
        roleDescription='Administrador'):
        """
        This method creates an admin user with the specified username, password,
        registration date, and role description. It requires the username, password,
        and registration date. The role description defaults to 'Administrador'.
        Raises ValueError if the username is not provided.
        :param username: Username for the admin user (should be an email for consistency)
        :param password: Password for the admin user
        :param regDate: Registration date for the admin user
        :param roleDescription: Description of the role (default is 'Administrador')
        :return: The created admin user instance
        """
        if not username:
            raise ValueError('El nombre de usuario es obligatorio.')
        
        role = Role.get_or_create_role(roleDescription)

        admin = self.model(
            User=username,
            registrationDate=regDate,
            roleID=role,
            is_staff=True,
            is_superuser=True
        )

        admin.set_password(password)
        admin.save(using=self._db)

        return admin

class Role(models.Model):
    roleID = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.Role'

    def __str__(self):
        return self.Description

    @classmethod
    def get_or_create_role(cls, description):
        role, _ = cls.objects.get_or_create(Description=description)
        return role

class WarrantyCustomer(models.Model):
    ID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=255, null=True, blank=True)
    LastName = models.CharField(max_length=50, null=True, blank=True)
    Address = models.CharField(max_length=255, null=True, blank=True)
    Zip = models.CharField(max_length=15, null=True, blank=True)
    EmailAddress = models.CharField(max_length=255, null=True, blank=True)
    PhoneNumber = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'Warranty.Customer'

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

class Users(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    id_user = models.AutoField(primary_key=True)
    User = models.CharField(max_length=255, unique=True)
    registrationDate = models.DateField(default=timezone.now)
    CustomerID = models.ForeignKey('WarrantyCustomer', on_delete=models.CASCADE)
    roleID = models.ForeignKey('Role', on_delete=models.CASCADE)

    # Required for Django auth
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'Users'  # This tells Django to use this field for login
    REQUIRED_FIELDS = []  # Add any other required fields here

    class Meta:
        db_table = 'Warranty.Users'

    def __str__(self):
        return self.Users

    @classmethod
    def getUsersAdmin(cls):
        users = cls.objects.all().values('id_user', 'User', 'password', 'registrationDate', 'CustomerID', 'roleID')
        return list(users)

class WarrantyStatus(models.Model):
    statusID = models.CharField(max_length=255, primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.warrantyStatus'

    def __str__(self):
        return self.description

    @classmethod
    def create_default_statuses(cls, purchaseDate=None):
        """
        Creates default statuses and returns the correct status based on purchaseDate.
        If purchaseDate is less than a year ago, returns 'Válida', else 'Inválida'.
        """
        
        defaults = [
            {'statusID': 0, 'description': 'Válida'},
            {'statusID': 1, 'description': 'Inválida'}
        ]
        for entry in defaults:
            cls.objects.get_or_create(statusID=entry['statusID'], defaults={'description': entry['description']})

        if purchaseDate:
            if isinstance(purchaseDate, str):
                try:
                    purchaseDate = date.fromisoformat(purchaseDate)
                except Exception:
                    pass
            today = date.today()
            if today - purchaseDate < timedelta(days=365):
                return cls.objects.get(description='Válida')
            else:
                return cls.objects.get(description='Inválida')
        return None
        
class Warranty(models.Model):
    NroGarantia = models.AutoField(primary_key=True)
    registerID = models.ForeignKey(Users, on_delete=models.CASCADE)
    branchID = models.ForeignKey('Branch', on_delete=models.CASCADE)
    ItemId = models.IntegerField()
    isRetail = models.BooleanField()
    purchaseDate = models.DateField()
    registrationDate = models.DateField(default=timezone.now)
    statusID = models.ForeignKey(WarrantyStatus, on_delete=models.CASCADE)
    productBrand = models.CharField(max_length=255)
    productBarcode = models.IntegerField()
    invoiceCopyPath = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.warranty'

    def __str__(self):
        return str(self.NroGarantia)

class Inventory(models.Model):
    customerID = models.IntegerField()
    itemID = models.IntegerField()
    isRetail = models.BooleanField()
    quantity = models.IntegerField()
    lastUpdate = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (('customerID', 'itemID', 'isRetail'),)
        db_table = 'Warranty.Inventory'    

class Issue(models.Model):
    IssueId = models.AutoField(primary_key=True)
    Issuesescription = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.Issue'

    def __str__(self):
        return self.Issuesescription

class TechnicalServiceStatus(models.Model):
    statusID = models.AutoField(primary_key=True)
    statusDescription = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.technicalServiceStatus'

    def __str__(self):
        return self.statusDescription

class TechnicalService(models.Model):
    registerID = models.AutoField(primary_key=True)
    warrantyID = models.ForeignKey(Warranty, on_delete=models.CASCADE)
    issueID = models.ForeignKey(Issue, on_delete=models.CASCADE)
    issueResolutionDetails = models.CharField(max_length=255)
    statusID = models.ForeignKey(TechnicalServiceStatus, on_delete=models.CASCADE)
    receptionDate = models.DateField()

    class Meta:
        db_table = 'Warranty.technicalService'

    def __str__(self):
        return str(self.registerID)
    
    @classmethod
    def open_case(cls, warranty_id, issue_id, issue_resolution_details, status_id, reception_date=None):
        """
        Opens a new technical service case for a specific warranty.
        """
        from datetime import date
        if reception_date is None:
            reception_date = date.today()
        try:
            warranty = Warranty.objects.get(NroGarantia=warranty_id)
            issue = Issue.objects.get(IssueId=issue_id)
            status = TechnicalServiceStatus.objects.get(statusID=status_id)
        except (Warranty.DoesNotExist, Issue.DoesNotExist, TechnicalServiceStatus.DoesNotExist):
            return None
        case = cls.objects.create(
            warrantyID=warranty,
            issueID=issue,
            issueResolutionDetails=issue_resolution_details,
            statusID=status,
            receptionDate=reception_date
        )
        return case

class MainCustomer(models.Model):
    AccountNumber = models.CharField(max_length=20, null=True)
    AccountTypeID = models.IntegerField(null=True)
    Address2 = models.CharField(max_length=50, null=True)
    AssessFinanceCharges = models.BooleanField(null=True)
    Company = models.CharField(max_length=50, null=True)
    Country = models.CharField(max_length=20, null=True)
    CustomDate1 = models.DateTimeField(null=True)
    CustomDate2 = models.DateTimeField(null=True)
    CustomDate3 = models.DateTimeField(null=True)
    CustomDate4 = models.DateTimeField(null=True)
    CustomDate5 = models.DateTimeField(null=True)
    CustomNumber1 = models.FloatField(null=True)
    CustomNumber2 = models.FloatField(null=True)
    CustomNumber3 = models.FloatField(null=True)
    CustomNumber4 = models.FloatField(null=True)
    CustomNumber5 = models.FloatField(null=True)
    CustomText1 = models.CharField(max_length=30, null=True)
    CustomText2 = models.CharField(max_length=30, null=True)
    CustomText3 = models.CharField(max_length=30, null=True)
    CustomText4 = models.CharField(max_length=30, null=True)
    CustomText5 = models.CharField(max_length=30, null=True)
    GlobalCustomer = models.BooleanField(null=True)
    HQID = models.IntegerField(null=True)
    LastStartingDate = models.DateTimeField(null=True)
    LastClosingDate = models.DateTimeField(null=True)
    LastUpdated = models.DateTimeField(null=True)
    LimitPurchase = models.BooleanField(null=True)
    LastClosingBalance = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    PrimaryShipToID = models.IntegerField(null=True)
    State = models.CharField(max_length=20, null=True)
    StoreID = models.IntegerField(null=True)
    ID = models.IntegerField(primary_key=True)
    LayawayCustomer = models.BooleanField(null=True)
    Employee = models.BooleanField(null=True)
    FirstName = models.CharField(max_length=255, null=True)
    LastName = models.CharField(max_length=50, null=True)
    Address = models.CharField(max_length=255, null=True)
    City = models.CharField(max_length=50, null=True)
    Zip = models.CharField(max_length=15, null=True)
    AccountBalance = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    CreditLimit = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    TotalSales = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    AccountOpened = models.DateTimeField(null=True)
    LastVisit = models.DateTimeField(null=True)
    TotalVisits = models.IntegerField(null=True)
    TotalSavings = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    CurrentDiscount = models.FloatField(null=True)
    PriceLevel = models.IntegerField(null=True)
    TaxExempt = models.BooleanField(null=True)
    Notes = models.TextField(null=True)
    Title = models.CharField(max_length=20, null=True)
    EmailAddress = models.CharField(max_length=255, null=True)
    DBTimeStamp = models.BinaryField(max_length=8, null=True)
    TaxNumber = models.CharField(max_length=20, null=True)
    PictureName = models.CharField(max_length=50, null=True)
    DefaultShippingServiceID = models.IntegerField(null=True)
    AutoID = models.IntegerField(null=True)
    PhoneNumber = models.CharField(max_length=30, null=True)
    FaxNumber = models.CharField(max_length=30, null=True)
    CashierID = models.IntegerField(null=True)
    SalesRepID = models.IntegerField(null=True)
    Vouchers = models.DecimalField(max_digits=19, decimal_places=4, null=True)
    SyncGuid = models.UUIDField(null=True)
    isRetail = models.BooleanField()

    class Meta:
        db_table = 'Main.Customer'
        unique_together = (('ID', 'isRetail'),)

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

class Branch(models.Model):
    branchID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(MainCustomer, on_delete=models.CASCADE)
    isRetail = models.BooleanField()
    RIFtype = models.CharField(max_length=255, default='J')
    RIF = models.IntegerField()
    companyName = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    branchDescription = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.Branch'

    def __str__(self):
        return self.companyName

class MainItem(models.Model):
    BinLocation = models.CharField(max_length=20)
    BuydownPrice = models.DecimalField(max_digits=19, decimal_places=4)
    BuydownQuantity = models.FloatField()
    CommissionAmount = models.DecimalField(max_digits=19, decimal_places=4)
    CommissionMaximum = models.DecimalField(max_digits=19, decimal_places=4)
    CommissionMode = models.IntegerField()
    CommissionPercentProfit = models.FloatField()
    CommissionPercentSale = models.FloatField()
    Description = models.CharField(max_length=30)
    FoodStampable = models.BooleanField()
    HQID = models.IntegerField()
    ItemNotDiscountable = models.BooleanField()
    LastReceived = models.DateTimeField(null=True)
    LastUpdated = models.DateTimeField()
    Notes = models.TextField(null=True)
    QuantityCommitted = models.FloatField()
    SerialNumberCount = models.IntegerField()
    TareWeightPercent = models.FloatField()
    ID = models.IntegerField(primary_key=True)
    ItemLookupCode = models.CharField(max_length=25)
    DepartmentID = models.IntegerField()
    CategoryID = models.IntegerField()
    MessageID = models.IntegerField()
    Price = models.DecimalField(max_digits=19, decimal_places=4)
    PriceA = models.DecimalField(max_digits=19, decimal_places=4)
    PriceB = models.DecimalField(max_digits=19, decimal_places=4)
    PriceC = models.DecimalField(max_digits=19, decimal_places=4)
    SalePrice = models.DecimalField(max_digits=19, decimal_places=4)
    SaleStartDate = models.DateTimeField(null=True)
    SaleEndDate = models.DateTimeField(null=True)
    QuantityDiscountID = models.IntegerField()
    TaxID = models.IntegerField()
    ItemType = models.IntegerField()
    Cost = models.DecimalField(max_digits=19, decimal_places=4)
    Quantity = models.FloatField()
    ReorderPoint = models.FloatField()
    RestockLevel = models.FloatField()
    TareWeight = models.FloatField()
    SupplierID = models.IntegerField()
    TagAlongItem = models.IntegerField()
    TagAlongQuantity = models.FloatField()
    ParentItem = models.IntegerField()
    ParentQuantity = models.FloatField()
    BarcodeFormat = models.IntegerField()
    PriceLowerBound = models.DecimalField(max_digits=19, decimal_places=4)
    PriceUpperBound = models.DecimalField(max_digits=19, decimal_places=4)
    PictureName = models.CharField(max_length=50)
    LastSold = models.DateTimeField(null=True)
    ExtendedDescription = models.TextField()
    SubDescription1 = models.CharField(max_length=30)
    SubDescription2 = models.CharField(max_length=30)
    SubDescription3 = models.CharField(max_length=30)
    UnitOfMeasure = models.CharField(max_length=10)
    SubCategoryID = models.IntegerField()
    QuantityEntryNotAllowed = models.BooleanField()
    PriceMustBeEntered = models.BooleanField()
    BlockSalesReason = models.CharField(max_length=30)
    BlockSalesAfterDate = models.DateTimeField(null=True)
    Weight = models.FloatField()
    Taxable = models.BooleanField()
    DBTimeStamp = models.BinaryField(max_length=8, null=True)
    BlockSalesBeforeDate = models.DateTimeField(null=True)
    LastCost = models.DecimalField(max_digits=19, decimal_places=4)
    ReplacementCost = models.DecimalField(max_digits=19, decimal_places=4)
    WebItem = models.BooleanField()
    BlockSalesType = models.IntegerField()
    BlockSalesScheduleID = models.IntegerField()
    SaleType = models.IntegerField()
    SaleScheduleID = models.IntegerField()
    Consignment = models.BooleanField()
    Inactive = models.BooleanField()
    LastCounted = models.DateTimeField(null=True)
    DoNotOrder = models.BooleanField()
    MSRP = models.DecimalField(max_digits=19, decimal_places=4)
    DateCreated = models.DateTimeField()
    Content = models.TextField()
    UsuallyShip = models.CharField(max_length=255)
    NumberFormat = models.CharField(max_length=50, null=True)
    ItemCannotBeRet = models.BooleanField(null=True)
    ItemCannotBeSold = models.BooleanField(null=True)
    IsAutogenerated = models.BooleanField(null=True)
    IsGlobalvoucher = models.BooleanField()
    DeleteZeroBalanceEntry = models.BooleanField(null=True)
    TenderID = models.IntegerField()
    SyncGuid = models.UUIDField()
    isRetail = models.BooleanField()

    class Meta:
        db_table = 'Main.Item'
        unique_together = (('ID', 'isRetail'),)

    def __str__(self):
        return self.Description