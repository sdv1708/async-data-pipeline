resource "aws_budgets_budget" "monthly" {
  name         = "monthly-budget"
  budget_type  = "COST"
  limit_amount = tostring(var.TODO_BUDGET_AMOUNT)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 100
    threshold_type      = "PERCENTAGE"
    notification_type   = "FORECASTED"

    subscriber_sns_topic_arns = [var.TODO_SNS_TOPIC_ARN_FOR_BUDGETS]
  }
}
