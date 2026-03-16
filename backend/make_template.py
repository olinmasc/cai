from docx import Document
import os

os.makedirs("templates", exist_ok=True)
doc = Document()

# We store the entire 16-page text in this variable to keep it 100% clean and crash-proof
TEMPLATE_TEXT = """INDEPENDENT AUDITORS' REPORT

To the Members of {{ company_name }}

Report on the Audit of the Standalone Financial Statements

Opinion
We have audited the financial statements of Standalone financial statements of {{ company_name }} ("the Company") which comprise the Balance Sheet as at {{ financial_year_end }}, and the Statement of Profit and Loss and Statement of Cash Flows for the year then ended, and notes to the financial statements, including a summary of significant accounting policies and other explanatory information.

In our opinion and to the best of our information and according to the explanations given to us, the aforesaid financial statements give the information required by the Companies Act, 2013 ("the Act") in the manner so required and give a true and fair view in conformity with the accounting principles generally accepted in India, of the state of affairs of the Company as at {{ financial_year_end }}, and its profits and cash flows for the year ended on that date.

Basis for Opinion
We conducted our audit in accordance with the Standards on Auditing (SAs) specified under section 143(10) of the Act. Our responsibilities under those standards are further described in the Auditor's Responsibilities for the Audit of the Financial Statements section of our report. We are independent of the Company in accordance with the Code of Ethics issued by the Institute of Chartered Accountants of India ("ICAI") together with the ethical requirements that are relevant to our audit of the financial statements under the provisions of the Act and the Rules thereunder, and We have fulfilled our other ethical responsibilities in accordance with these requirements and the Code of Ethics. We believe that the audit evidence we have obtained is sufficient and appropriate to provide a basis for our opinion.

Emphasis
We draw attention to Note [X] in the financial statements, which describes [briefly describe the matter being emphasized, such as a significant uncertainty, a new accounting policy, a change in estimates, etc.]. Our opinion is not modified in respect of this matter.

Key Audit Matters
We have determined the following area to be a key audit matter to be communicated in our report. The matter was addressed in the context of our audit of the financial statements as a whole, and in forming our opinion thereon.

Other Information
The Company's management and Board of Directors are responsible for the other information. The other information comprises the information included in the Director's report but does not include the financial statements and the Auditors' report thereon. Our opinion on the financial statements does not cover the other information and we do not express any form of assurance conclusion thereon.

In connection with our audit of the financial statements, our responsibility is to read the other information and, in doing so, consider whether the other information is materially inconsistent with the standalone financial statements, or our knowledge obtained in the audit or otherwise appears to be materially misstated. If, based on the work we have performed, we conclude that there is a material misstatement of this other information, we are required to report that fact. We have nothing to report in this regard.

Responsibility of Management for Standalone Financial Statements
The Company's management and Board of Directors are responsible for the matters stated in section 134(5) of the Act with respect to the preparation of these financial statements that give a true and fair view of the state of affairs, profit/loss of the Company in accordance with the accounting principles generally accepted in India, including the accounting Standards specified under section 133 of the Act. This responsibility also includes maintenance of adequate accounting records in accordance with the provisions of the Act for safeguarding of the assets of the Company and for preventing and detecting frauds and other irregularities; selection and application of appropriate accounting policies; making judgments and estimates that are reasonable and prudent; and design, implementation and maintenance of adequate internal financial controls, that were operating effectively for ensuring the accuracy and completeness of the accounting records, relevant to the preparation and presentation of the financial statement that give a true and fair view and are free from material misstatement, whether due to fraud or error.

In preparing the financial statements, management and Board of Directors are responsible for assessing the Company's ability to continue as a going concern, disclosing, as applicable, matters related to going concern and using the going concern basis of accounting unless management either intends to liquidate the Company or to cease operations, or has no realistic alternative but to do so.

The Board of Directors are also responsible for overseeing the company's financial reporting process.

Auditor's Responsibilities for the Audit of the Standalone Financial Statements
Our objectives are to obtain reasonable assurance about whether the financial statements as a whole are free from material misstatement, whether due to fraud or error, and to issue an auditor's report that includes our opinion. Reasonable assurance is a high level of assurance, but is not a guarantee that an audit conducted in accordance with SAs will always detect a material misstatement when it exists. Misstatements can arise from fraud or error and are considered material if, individually or in the aggregate, they could reasonably be expected to influence the economic decisions of users taken on the basis of these financial statements.

As part of an audit in accordance with SAs, we exercise professional judgment and maintain professional skepticism throughout the audit. We also:
* Identify and assess the risks of material misstatement of the financial statements, whether due to fraud or error, design and perform audit procedures responsive to those risks, and obtain audit evidence that is sufficient and appropriate to provide a basis for our opinion. The risk of not detecting a material misstatement resulting from fraud is higher than for one resulting from error, as fraud may involve collusion, forgery, intentional omissions, misrepresentations, or the override of internal control.
* Obtain an understanding of internal control relevant to the audit in order to design audit procedures that are appropriate in the circumstances, Under Section 143(3)(i) of the Act, we are also responsible for expressing an opinion on whether the company has adequate internal financial controls system with reference to financial statements in place and the operating effectiveness of such controls.
* Evaluate the appropriateness of accounting policies used and the reasonableness of accounting estimates and related disclosures made by management.
* Conclude on the appropriateness of management's use of the going concern basis of accounting and, based on the audit evidence obtained, whether a material uncertainty exists related to events or conditions that may cast significant doubt on the Company's ability to continue as a going concern. If we conclude that a material uncertainty exists, we are required to draw attention in our auditor's report to the related disclosures in the financial statements or, if such disclosures are inadequate, to modify our opinion. Our conclusions are based on the audit evidence obtained up to the date of our auditor's report. However, future events or conditions may cause the Company to cease to continue as a going concern.
* Evaluate the overall presentation, structure, and content of the financial statements, including the disclosures, and whether the financial statements represent the underlying transactions and events in a manner that achieves fair presentation.

We communicate with those charged with governance regarding, among other matters, the planned scope and timing of the audit and significant audit findings, including any significant deficiencies in internal control that we identify during our audit.

We also provide those charged with governance with a statement that we have complied with relevant ethical requirements regarding independence, and to communicate with them all relationships and other matters that may reasonably be thought to bear on our independence, and where applicable, related safeguards.

Report on Other Legal and Regulatory Requirements
1. As required by the Companies (Auditor's Report) Order, 2020 ("the Order") issued by the Central Government in terms of Section 143(11) of the Act we give in the "Annexure A" a statement on the matters specified in paragraphs 3 and 4 of the Order.

2. As required by Section 143(3) of the Act, we report that:
(a) We have sought and obtained all the information and explanations which to the best of our knowledge and belief were necessary for the purposes of our audit;
(b) In our opinion, proper books of account as required by law have been kept by the Company so far as it appears from the examination of those books;
(c) The financial statements dealt with by this Report are in agreement with the books of accounts.
(d) In our opinion, the aforesaid financial statements comply with the Accounting Standards specified under Section 133 of the Act, read with Rule 7 of the Companies (Accounts) Rules, 2014.
(e) On the basis of the written representations received from the directors as on {{ financial_year_end }} taken on record by the Board of Directors, none of the directors is disqualified as on {{ financial_year_end }} from being appointed as a director in terms of Section 164 (2) of the Act.
(f) with respect to the adequacy of the internal financial controls over financial reporting of the Company and the operating effectiveness of such controls, refer to our separate report in "Annexure B"; and
(g) The provisions of Section 197 read with Schedule V of the Act are not applicable to the Company for the period ended {{ financial_year_end }} since the Company is not a public company as defined under section 2(71) of the Act. Accordingly, reporting under section 197(16) is not applicable.
(h) With respect to the other matters to be included in the Auditor's Report in accordance with Rule 11 of the Companies (Audit and Auditors) Rules, 2014, in our opinion and to the best of our information and according to the explanations given to us:
a) The Company does not have any pending litigations which would impact its financial position.
b) The Company did not have any long-term contracts including derivative contracts for which there were any material foreseeable losses.
c) There were no amounts which were required to be transferred to the Investor Education and Protection Fund by the Company.
d) (a) The Management has represented that, to the best of its knowledge and belief, no funds (which are material either individually or in the aggregate) have been advanced or loaned or invested (either from borrowed funds or share premium or any other sources or kind of funds) by the Company to or in any other person or entity, including foreign entity ("Intermediaries"), with the understanding, whether recorded in writing or otherwise, that the Intermediary shall, whether, directly or indirectly lend or invest in other persons or entities identified in any manner whatsoever by or on behalf of the Company ("Ultimate Beneficiaries") or provide any guarantee, security or the like on behalf of the Ultimate Beneficiaries;
(b) The Management has represented, that, to the best of its knowledge and belief, no funds (which are material either individually or in the aggregate) have been received by the Company from any person or entity, including foreign entity ("Funding Parties"), with the understanding, whether recorded in writing or otherwise, that the Company shall, whether, directly or indirectly, lend or invest in other persons or entities identified in any manner whatsoever by or on behalf of the Funding Party ("Ultimate Beneficiaries") or provide any guarantee, security or the like on behalf of the Ultimate Beneficiaries;
(c) Based on the audit procedures that have been considered reasonable and appropriate in the circumstances, nothing has come to our notice that has caused us to believe that the representations under sub-clause (i) and (ii) of Rule 11(e), as provided under (a) and (b) above, contain any material misstatement.
e) The company did not declare any dividend during the year.
f) Based on our examination, which included test checks, the Company has used accounting software for maintaining its books of account for the financial year ended {{ financial_year_end }} which has a feature of recording audit trail (edit log) facility and the same has been in operation throughout the year for all relevant transactions recorded in the software. Further, during the course of our audit we did not come across any instance of the audit trail feature being tampered with; As proviso to Rule 3(1) of the Companies (Accounts) Rules, 2014 is applicable from April 1, 2023, reporting under Rule 11(g) of the Companies (Audit and Auditors) Rules, 2014 on preservation of audit trail as per the statutory requirements for retention of the record is not applicable for the financial year ended {{ financial_year_end }};

For {{ ca_firm_name }}
Chartered Accountants
Firm Registration No.: {{ firm_registration_no }}

{{ partner_name }}
Partner
Membership No.: {{ membership_no }}
Place: {{ sign_place }}
Date: {{ sign_date }}
UDIN: 

---

Annexure-A to the Auditor's Report

The Annexure referred to in Independent Auditors' Report to the members of {{ company_name }} ("the Company"), on the Standalone financial statements for the year ended {{ financial_year_end }}, we report that:

Based on the audit procedures performed for the purpose of reporting a true and fair view on the Standalone financial statements of the Company and taking into consideration the information and explanations given to us and the books of account and other records examined by us in the normal course of audit, and to the best of our knowledge and belief, we report that:

(i)
(a) The Company has maintained proper records showing full particulars, including quantitative details and situation of property, plant and equipment.
(b) The Company has maintained proper records showing full particulars of intangible assets as reflected in books.
(c) As explained to us, the Property, plant and equipment have been physically verified by the management in a phased periodical manner, which in our opinion is reasonable, having regard to the size of the company and nature of its assets. No material discrepancies are noticed on such physical verification.
(d) According to the information and explanations given to us and on the basis of our examination of the records of the Company, the title deeds of immovable properties included in property, plant and equipment are held in the name of the Company. In respect of immovable properties taken on lease and disclosed as right-of-use-assets in the standalone financial statements, the lease agreements are in the name of the Company.
(e) The Company has not revalued its property, plant and equipment or intangible assets during the period ended {{ financial_year_end }}.
(f) There are no proceedings initiated or are pending against the Company for holding any benami property under the Prohibition of Benami Property Act, 1988 and rules made thereunder.

(ii) (a) As explained to us, the inventories are physically verified during the year by the Management at reasonable intervals and no material discrepancies are noticed on such physical verification.
(b) According to information and explanation given to us, the Company has not been sanctioned working capital limits in excess of Rs. 5 Crores, in aggregate, at any time during the year, from banks or financial institutions on the basis of security of the current assets of the Company.

(iii) In our opinion and according to the information and explanation given to us, the Company has not entered into any transaction covered under section 185 of the Act. Further, based on the information and explanation given to us, the Company has complied with the provision of Section 186 of the Act in respect of granting loans, making investments and providing guarantees and securities.

(iv) According to information and explanations given to us, the Company has not accepted any deposit from the public therefore the question of complying with the provisions of sections 73 to 76 of the Act and rules framed there under does not arise.

(v) We have broadly reviewed the records maintained by the Company pursuant to the rules made by the Central Government for the maintenance of cost records under Section 148(1) of the Act, related to the manufacturing activities, and are of the opinion that prima facie, the specified accounts and records have been made and maintained. We have not, however, made a detailed examination of the same.

(vi) According to the information and explanations given to us, in respect of statutory dues: -
(a) According to the records of the Company, undisputed statutory dues including Provident Fund, Investors Education and Protection Fund, Employees' State Insurance, Income-Tax, Customs Duty, Excise Duty, Cess and other material Statutory Dues, to the extent applicable in the case of the company, have been generally regularly deposited with the appropriate authorities except slight delay in Income Tax. According to the information and explanations given to us, no undisputed amounts payable in respect of the aforesaid dues were outstanding as at the last day of the year for a period of more than six months from the date of becoming payable.
(b) According to the information and explanations given to us, the dues outstanding of income tax which have not been deposited as on {{ financial_year_end }} on account of any dispute are given below:

{% for dispute in tax_disputes %}
• Statute: {{ dispute.statute }}
• Nature of Dues: {{ dispute.nature }}
• Gross Amount: Rs. {{ dispute.gross }}
• Amount Deposited: Rs. {{ dispute.deposited }}
• Period: {{ dispute.period }}
• Forum: {{ dispute.forum }}
---------------------------------------------------------
{% endfor %}

(vii) There were no transactions relating to previously unrecorded income that were surrendered or disclosed as income in the tax assessment under the Income Tax Act, 1961 (43 of 1961) during the year.

(viii) In our opinion and on the basis of information and explanations given to us and based on our examination of the books of account of the Company:
a. During the year, the Company has not defaulted in repayment of loans or other borrowings or in the payment of interest to any lender;.
b. The Company has not been declared wilful defaulter by any bank or financial institution or any other lenders;
c. According to the information and explanations given to us, term loans availed by the Company were applied for the purposes for which the loans were obtained.
d. According to the information and explanations given to us, and the procedures performed by us, and on an overall examination of the standalone financial statements of the Company, We report that no funds raised on short term basis have been used for long term purposes by the Company;
e. The Company has not taken any funds from any entity or person on account of or to meet obligation of its Associate.
f. The Company has not raised loans during the year on the pledge of securities held in its Associate or subsidiary company. The Company does not have any joint venture.

(ix) a. In our opinion and according to information and explanation given by the management, the Company did not raise money by way of initial public offer or further public offer (including debt instruments) during the year and hence reporting under the clause 3(x)(a) of the Order is not applicable.
b. The Company has not made any preferential allotment or private placement of shares or convertible debentures (fully, partially, or optionally) during the year and accordingly, reporting under paragraph 3(x)(b) of the Order is not applicable.

(x) a. No fraud by the Company or on the Company by its officers or employees has been noticed or reported during the period covered under audit.
b. No report under sub-section (12) of section 143 of the Act, has been filed in Form ADT-4 as prescribed under Rule 13 of Companies (Audit and Auditors) Rules, 2014 (as amended from time to time) with the Central Government, during the year and up to the date of this report.
c. According to the information and explanation given to us and based on our examination of the books of account of the company, no whistleblower complaints have been received during the year by the company. Accordingly reporting under paragraph xi(c) of the order is not applicable.

(xi) The Company is not a Nidhi Company. Accordingly, provision of clause 3(xii) (a, b & c) of the Order is not applicable.

(xii) In our opinion, all transactions with the related parties are in compliance with Section 188 of the Act, where applicable, and the requisite details have been disclosed in the financial statements, as required by the applicable accounting standards. Further, in our opinion, the company is not required to constitute audit committee under section 177 of the Act.

(xiii) According to the information and explanation given to us, the Company is not required to have an internal audit system under Section 138 of the Act and consequently, does not have an internal audit system. Accordingly, reporting under clause 3 (xiv) of the Order is not applicable to the Company.

(xiv) In our opinion and according to the information and explanations given to us, during the year, the Company has not entered into any non-cash transactions with its directors or persons connected with him and hence reporting under clause (xv) of Paragraph 3 of the Order is not applicable to the Company.

(xv) According to the information and explanation given to us and based on our examination of the books and records of the Company:
a. The Company is not required to be registered under Section 45-IA of the Reserve Bank of India Act, 1934;
b. The Company has not conducted any non-banking financial or housing finance activities during the year;
c. The Company is not a Core Investment Company (hereinafter referred to as "CIC") as defined in the Core Investment Companies (Directions), 2016, as amended from time to time, issued by the Reserve Bank of India and hence, reporting under paragraph 3(xvi)(c) of the Order is not applicable; and
d. In our opinion and based on the representation received from the management, there is no core investment company within the Group (as defined in the Core Investment Companies (Reserve Bank) Directions, 2016) and accordingly, reporting under paragraph 3(xvi)(d) of the Order is not applicable.

(xvi) Based on the examination of the books of accounts, we report that the Company has not incurred cash losses in the current financial year covered under our audit or in the immediately preceding financial year.

(xvii) There has been resignation of the statutory auditors during the year, there were no issues, objections or concerns raised by the outgoing auditors

(xviii) According to the information and explanations given to us and based on the financial ratios, ageing and expected dates of realization of financial assets and payment of financial liabilities, other information accompanying standalone financial statements, our knowledge of the Board of Directors and management plans and based on our examination of the evidence supporting the assumptions, nothing has come to our attention, which causes us to believe that any material uncertainty exists as on the date of the audit report that Company is not capable of meeting its liabilities existing at the date of balance sheet as and when they fall due within a period of one year from the balance sheet date. We, however, state that this is not an assurance as to the future viability of the Company. We further state that our reporting is based on the facts up to the date of the audit report and we neither give any guarantee nor any assurance that all liabilities falling due within a period of one year from the balance sheet date, will get discharged by the Company as and when they fall due.

(xix) According to the information and explanations provided to us, the Company does not have any unspent amounts towards Corporate Social responsibility in respect of any ongoing or other than ongoing project at the end of the financial year. Accordingly, reporting under clause 3(xx) of the Order is not applicable to the company.

(xx) The reporting under clause 3 (xxi) of the Order is not applicable in respect of the audit of Standalone financial statements of the Company. Accordingly, no comment has been included in respect of the said clause under this report.

For {{ ca_firm_name }}
Chartered Accountants
Firm Registration No.: {{ firm_registration_no }}

{{ partner_name }}
Partner
Membership No.: {{ membership_no }}
Place: {{ sign_place }}
Date: {{ sign_date }}
UDIN: 

---

Annexure - B to the Auditors' Report

Report on the Internal Financial Controls under Clause (i) of Sub-section 3 of Section 143 of the Companies Act, 2013 ("the Act")
(Referred to in paragraph 2(f) under "Report on other Legal and Regulatory Requirements" Section of our report of even date)

We have audited the internal financial controls over financial reporting of {{ company_name }} ("the Company") as of {{ financial_year_end }} in conjunction with our audit of the financial statements of the Company for the year ended on that date.

In our opinion, the company has, in all material respect, adequate internal financial control with reference to financial statement and such internal financial controls were operating effectively as at {{ financial_year_end }} based on the internal financial control with reference to financial statement criteria established by the company considering the essential components of internal control stated in the Guidance Notes on Audit of Internal financial Controls Over Financial Reporting issued by The Institute of Chartered Accountant of India (the "Guidance Note").

Management's Responsibility for Internal Financial Controls
The Company's management is responsible for establishing and maintaining internal financial controls based on the internal control over financial reporting criteria established by the Company considering the essential components of internal control stated in the Guidance Note on Audit of Internal Financial Controls over Financial Reporting issued by the Institute of Chartered Accountants of India ('ICAI'). These responsibilities include the design, implementation and maintenance of adequate internal financial controls that were operating effectively for ensuring the orderly and efficient conduct of its business, including adherence to company's policies, the safeguarding of its assets, the prevention and detection of frauds and errors, the accuracy and completeness of the accounting records, and the timely preparation of reliable financial information, as required under the Companies Act, 2013.

Auditors' Responsibility
Our responsibility is to express an opinion on the Company's internal financial controls with reference to financial statement based on our audit. We conducted our audit in accordance with the Guidance Note on Audit of Internal Financial Controls over Financial Reporting (the "Guidance Note") and the Standards on Auditing, issued by ICAI and deemed to be prescribed under section 143(10) of the Companies Act, 2013, to the extent applicable to an audit of internal financial controls, both applicable to an audit of Internal Financial Controls and, both issued by the Institute of Chartered Accountants of India. Those Standards and the Guidance Note require that we comply with ethical requirements and plan and perform the audit to obtain reasonable assurance about whether adequate internal financial controls over financial reporting was established and maintained and if such controls operated effectively in all material respects.

Our audit involves performing procedures to obtain audit evidence about the adequacy of the internal financial controls system over financial reporting and their operating effectiveness. Our audit of internal financial controls over financial reporting included obtaining an understanding of internal financial controls over financial reporting, assessing the risk that a material weakness exists, and testing and evaluating the design and operating effectiveness of internal control based on the assessed risk. The procedures selected depend on the auditor's judgment, including the assessment of the risks of material misstatement of the financial statements, whether due to fraud or error.

We believe that the audit evidence we have obtained is sufficient and appropriate to provide a basis for our audit opinion on the Company's internal financial controls system over financial reporting.

Meaning of Internal Financial Controls Over Financial Reporting
A company's internal financial control over financial reporting is a process designed to provide reasonable assurance regarding the reliability of financial reporting and the preparation of financial statements for external purposes in accordance with generally accepted accounting principles. A company's internal financial control over financial reporting includes those policies and procedures that:-
(1) pertain to the maintenance of records that, in reasonable detail, accurately and fairly reflect the transactions and dispositions of the assets of the company;
(2) provide reasonable assurance that transactions are recorded as necessary to permit preparation of financial statements in accordance with generally accepted accounting principles, and that receipts and expenditures of the company are being made only in accordance with authorizations of management and directors of the company; and
(3) provide reasonable assurance regarding prevention or timely detection of unauthorized acquisition, use, or disposition of the company's assets that could have a material effect on the financial statements.

Inherent Limitations of Internal Financial Controls Over Financial Reporting
Because of the inherent limitations of internal financial controls over financial reporting, including the possibility of collusion or improper management override of controls, material misstatements due to error or fraud may occur and not be detected. Also, projections of any evaluation of the internal financial controls over financial reporting to future periods are subject to the risk that the internal financial control over financial reporting may become inadequate because of changes in conditions, or that the degree of compliance with the policies or procedures may deteriorate.

For {{ ca_firm_name }}
Chartered Accountants
Firm Registration No.: {{ firm_registration_no }}

{{ partner_name }}
Partner
Membership No.: {{ membership_no }}
Place: {{ sign_place }}
Date: {{ sign_date }}
UDIN: 
"""

# We process the text line-by-line to maintain paragraphs!
for line in TEMPLATE_TEXT.split('\n'):
    doc.add_paragraph(line)

doc.save("templates/statutory_audit_template.docx")
print("✅ Pristine, FULL 16-PAGE crash-proof template successfully generated!")
