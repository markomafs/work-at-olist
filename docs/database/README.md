# Database Documentation

## Models

See [MER](MER.pdf) schema

All Tables/Models must have:
* `id` unique primary key identifier
* `created_at` timestamp representing when each row was created
* `updated_at` timestamp representing when each row was updated

#### PhoneNumber

* Responsible for all phone numbers
  * Destination phone numbers
  * Origin phone numbers
* `area_code` is the Brazilian Region identifier
* `phone_number` is the number itself with 8 or 9 digits
* `area_code` was separated from `phone_number` for reports or aggregation
* Unique KEY between (`area_code` and `phone_number`) to avoid duplication

#### Call

* Responsible for all calls made
  * One Row peer `call_code`
* `call_code` is a unique identifier received not created by billing service
* `started_at` is the timestamp that call was started
* `ended_at` is the timestamp that call was ended
* `fk_origin_phone_number` is a reference for PhoneNumber table representing call origin
* `fk_destination_phone_number` is a reference for PhoneNumber table representing call destination

#### BillingRule

* Responsible for rules of billing based on time interval
  * Avoid update billing rule, create another instead
    * It won't cause billing impact
    * But it could cause misunderstand billing, i.e.: 2 call with the same rule with different cost applied
  * Keep in mind that you shouldn't have 2 actives rules with conflicting ranges, i.e.: (8:00 - 10:00 and 9:00 - 11:00)
    * It can cause unexpected billing calculation
* `time_start` represents start time that this rule will start to apply
* `time_end` represents start time that this rule will stop to apply
* `fixed_charge` is the fixed charge that will apply for that period
* `by_minute_charge` is the charge that will apply based on minutes on call
* `is_active` flag that represents if that rule is available or not

#### Billing

* Responsible for billing each call
  * One call can have 1 or more billing rows based on billing rules
* `fk_call` is a reference for Call table representing call information
* `fk_billing_rule` is a reference for BillingRule table representing rules for this billing
* `amount` is the calculated amount for this call with this rule
* `hours` is the summarized hours for this billing
* `minutes` is the summarized minutes for this billing
* `seconds` is the summarized seconds for this billing