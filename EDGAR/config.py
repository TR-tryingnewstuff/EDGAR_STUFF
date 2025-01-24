
HEADERS = {'User-Agent': 'thomas.rigou@etu.univ-paris1.fr'}
DATAPATH = '/Users/main/Desktop/EDGAR/EDGAR_DATA/'
CIK_DF = "/Users/main/Desktop/EDGAR/CIK.pq"

# ================== FILINGS SECTIONS ============================
# ! There can be no ".", it can also take the form {"ItemX:", "ItemX-"}
# ! There are no other "Item" near it
# ! Sometimes titles do not mention the Item and are in all Uppercase alone on a line, ex : \nBUSINESS\n

items_10k = {
    "1": "Item1[\.\:\-,]{0,3}Business(?!(.{0,10}item)|(and)|(\")|(of))",
    "1A": "Item1\.?A[\.\:\-,]{0,3}RiskFactors(?!(.{0,10}item)|(and)|(\")|(of))",
    "1B": "Item1\.?B[\.\:\-,]{0,3}UnresolvedStaffComments(?!(.{0,10}item)|(and)|(\")|(of))",
    "1C": "Item1\.?C[\.\:\-,]{0,3}Cybersecurity(?!(.{0,10}item)|(and)|(\")|(of))",
    "2": "Item2[\.\:\-,]{0,3}Properties(?!(.{0,10}item)|(and)|(\")|(of))",
    "3": "Item3[\.\:\-,]{0,3}LegalProceedings(?!(.{0,10}item)|(and)|(\")|(of))",
    "4": "Item4[\.\:\-,]{0,3}MineSafetyDisclosures(?!(.{0,10}item)|(and)|(\")|(of))",
    "5": "Item5[\.\:\-,]{0,3}MarketforRegistrant'?sCommonEquity,RelatedStockholderMattersandIssuerPurchasesofEquitySecurities(?!(.{0,10}item)|(and)|(\")|(of))",
    "6": "Item6[\.\:\-,]{0,3}(\[?Reserved\]?|selectedfinancialdata)(?!(.{0,10}item)|(and)|(\")|(of))",
    "7": "Item7[\.\:\-,]{0,3}Management.?sDiscussionandAnalysisofFinancialConditionandResultsofOperations(?!(.{0,10}item)|(and)|(\")|(of))",
	"7A": "Item7\.?A[\.\:\-,]{0,3}QuantitativeandQualitativeDisclosures?AboutMarketRisk(?!(.{0,10}item)|(and)|(\")|(of))",
    "8": "Item8[\.\:\-,]{0,3}FinancialStatementsandSupplementaryData(?!(.{0,10}item)|(and)|(\")|(of))",
    "9": "Item9[\.\:\-,]{0,3}ChangesinandDisagreementswithAccountantsonAccountingandFinancialDisclosure(?!(.{0,10}item)|(and)|(\")|(of))",
    "9A": "Item9\.?A[\.\:\-,]{0,3}ControlsandProcedures(?!(.{0,10}item)|(and)|(\")|(of))",
    "9B": "Item9\.?B[\.\:\-,]{0,3}Other Information(?!(.{0,10}item)|(and)|(\")|(of))",
    "9C": "Item9\.?C[\.\:\-,]{0,3}DisclosureRegardingForeignJurisdictionsthatPreventInspections(?!(.{0,10}item)|(and)|(\")|(of))",
    "10": "Item10[\.\:\-,]{0,3}Directors,?ExecutiveOfficersandCorporateGovernance(?!(.{0,10}item)|(and)|(\")|(of))",
    "11": "Item11[\.\:\-,]{0,3}ExecutiveCompensation(?!(.{0,10}item)|(and)|(\")|(of))",
    "12": "Item12[\.\:\-,]{0,3}SecurityOwnershipofCertainBeneficialOwnersandManagementandRelatedStockholderMatters(?!(.{0,10}item)|(and)|(\")|(of))",
    "13": "Item13[\.\:\-,]{0,3}CertainRelationshipsandRelatedTransactions,?andDirectorIndependence(?!(.{0,10}item)|(and)|(\")|(of))",
    "14": "Item14[\.\:\-,]{0,3}PrincipalAccountantFeesandServices(?!(.{0,10}item)|(and)|(\")|(of))",
    "15": "Item15[\.\:\-,]{0,3}ExhibitsandFinancialStatementSchedules(?!(.{0,10}item)|(and)|(\")|(of))",
    "16": "Item16[\.\:\-,]{0,3}Form10-KSummary(?!(.{0,10}item)|(and)|(\")|(of))"
}

items_10q = {
    # Part I — Financial Information
    "1": r"Item1[\.\:\-,]{0,3}FinancialStatements(?!(.{0,10}item)|(and)|(\")|(of))",
    "2": r"Item2[\.\:\-,]{0,3}Management['’]?sDiscussionandAnalysisofFinancialConditionandResultsofOperations(?!(.{0,10}item)|(and)|(\")|(of))",
    "3": r"Item3[\.\:\-,]{0,3}QuantitativeandQualitativeDisclosuresAboutMarketRisk(?!(.{0,10}item)|(and)|(\")|(of))",
    "4": r"Item4[\.\:\-,]{0,3}ControlsandProcedures(?!(.{0,10}item)|(and)|(\")|(of))",
    
    # Part II — Other Information
    "1_": r"Item1[\.\:\-,]{0,3}LegalProceedings(?!(.{0,10}item)|(and)|(\")|(of))",
    "1A_": r"Item\.1A[\.\:\-,]{0,3}RiskFactors(?!(.{0,10}item)|(and)|(\")|(of))",
    "2_": r"Item2[\.\:\-,]{0,3}UnregisteredSalesofEquitySecuritiesandUseofProceeds(?!(.{0,10}item)|(and)|(\")|(of))",
    "3_": r"Item3[\.\:\-,]{0,3}DefaultsUponSeniorSecurities(?!(.{0,10}item)|(and)|(\")|(of))",
    "4_": r"Item4[\.\:\-,]{0,3}MineSafetyDisclosures(?!(.{0,10}item)|(and)|(\")|(of))",
    "5_": r"Item5[\.\:\-,]{0,3}OtherInformation(?!(.{0,10}item)|(and)|(\")|(of))",
    "6_": r"Item6[\.\:\-,]{0,3}Exhibits(?!(.{0,10}item)|(and)|(\")|(of))"
}
