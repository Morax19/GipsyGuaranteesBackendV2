from django.db import models
from django.utils import timezone

class Role(models.Model):
    RoleID = models.AutoField(primary_key=True)
    Description = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.Role'

    def __str__(self):
        return self.Description 

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

class WarrantyStatus(models.Model):
    statusID = models.CharField(max_length=255, primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'Warranty.warrantyStatus'

    def __str__(self):
        return self.description

class Users(models.Model):
    userID = models.AutoField(primary_key=True)
    Users = models.CharField(max_length=255)
    Password = models.CharField(max_length=255)
    registrationDate = models.DateField(default=timezone.now)
    CustomerID = models.ForeignKey(WarrantyCustomer, on_delete=models.CASCADE)
    roleID = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Warranty.Users'

    def __str__(self):
        return self.Users
    
class Warranty(models.Model):
    NroGarantia = models.AutoField(primary_key=True)
    registerID = models.ForeignKey(Users, on_delete=models.CASCADE)
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

class Branch(models.Model):
    branchID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(WarrantyCustomer, on_delete=models.CASCADE)
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