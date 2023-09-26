# EC2 Uptime Report

Generate a monthly uptime report for AWS EC2 instances based on the `StatusCheckFailed` metric from CloudWatch. The report is generated as a CSV, saved to an S3 bucket, and then an email notification with a link to the report is sent.

## Prerequisites

- An AWS account.
- An S3 bucket to store the monthly reports.
- AWS Simple Email Service (SES) configured to send emails.
- AWS Lambda to run the report generation script.
- AWS CloudWatch (Amazon EventBridge) to schedule the monthly execution of the Lambda function.

## Deployment Steps

1. **AWS Lambda**:
    - Navigate to the AWS Lambda console.
    - Create a new Lambda function.
    - Use the provided Python script (`uptime_report.py`) as the Lambda function code.
    - Set the Lambda memory to at least 256MB and the timeout to a suitable value (e.g., 5 minutes) depending on the number of EC2 instances you have.
    - Configure an environment variable for the Lambda function:
      - `BUCKET_NAME`: Name of your S3 bucket where reports will be stored.
    - Create an EventBridge (CloudWatch Events) rule to trigger this Lambda function on the first day of every month.

2. **IAM Role for Lambda**:
    Create an IAM role for the Lambda function with the following permissions:
    - EC2: `DescribeInstances` to fetch instance details.
    - CloudWatch: `GetMetricData` to retrieve `StatusCheckFailed` metric data.
    - S3: `PutObject` to save reports in the specified S3 bucket.
    - SES: `SendEmail` to send email notifications.
   
   Example IAM policy:
   ```json
   {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "ec2:DescribeInstances",
                  "cloudwatch:GetMetricData",
                  "s3:PutObject",
                  "ses:SendEmail"
              ],
              "Resource": "*"
          }
      ]
   }
   ```

3. **S3 Bucket**:
   Ensure your S3 bucket has the correct bucket policy to allow the Lambda function to store reports. Also, if you wish to make the reports publicly accessible, configure the bucket policy accordingly.

4. **SES (Simple Email Service)**:
    - Verify the email address from which you'll send notifications.
    - Ensure you're within the SES sending limits and that the recipient email address isn't on the SES suppression list.

5. **AWS CloudWatch (EventBridge)**:
    - Set up a rule to trigger the Lambda function on a monthly schedule.
    - For the event source, choose `EventBridge (CloudWatch Events)` and create a new rule with a cron expression for the desired schedule.

## Notes

- Ensure you handle AWS service limits (e.g., API call limits) if you have a large number of EC2 instances.
- For extensive use, consider setting up proper error handling and notifications.
- Keep AWS costs in mind, especially with respect to the number of CloudWatch metric data points retrieved and the storage of reports in S3.

## License

This project is released under the MIT License. Please refer to the `LICENSE` file for detailed terms and conditions.

## Contribution

Contributions are welcome! Please raise an issue or submit a pull request if you'd like to improve this project.

