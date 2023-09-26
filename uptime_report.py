import boto3
import csv
from datetime import datetime, timedelta
from io import StringIO

def generate_uptime_report():
    # Initialize clients for CloudWatch, S3, and SES
    cw_client = boto3.client('cloudwatch')
    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses')
    
    # Constants for your setup
    BUCKET_NAME = "your-s3-bucket-name"
    S3_KEY = "ec2_uptime_reports/uptime_report_{}.csv".format(datetime.now().strftime('%Y_%m'))
    EMAIL_RECIPIENT = "your-email@example.com"
    EMAIL_SENDER = "sender-email@example.com"
    
    # Calculate the start and end time for the report (last month's data)
    end_time = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_time = (end_time - timedelta(days=1)).replace(day=1)
    
    # Fetch all EC2 instance IDs
    ec2_client = boto3.client('ec2')
    instances = ec2_client.describe_instances()
    instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]
    
    # Create CSV in-memory file
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(['Instance ID', 'Uptime Percentage'])
    
    for instance_id in instance_ids:
        # Fetch StatusCheckFailed metric data
        metric_data = cw_client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'status_check_failed',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/EC2',
                            'MetricName': 'StatusCheckFailed',
                            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}]
                        },
                        'Period': 300,
                        'Stat': 'Average',
                    },
                    'ReturnData': True
                }
            ],
            StartTime=start_time,
            EndTime=end_time
        )
        
        # Calculate uptime based on metric data
        data_points = metric_data['MetricDataResults'][0]['Values']
        total_intervals = len(data_points)
        failed_intervals = sum(1 for dp in data_points if dp > 0)
        uptime_percentage = ((total_intervals - failed_intervals) / total_intervals) * 100
        csv_writer.writerow([instance_id, "{:.2f}%".format(uptime_percentage)])
    
    # Save CSV to S3
    output.seek(0)
    s3_client.put_object(Bucket=BUCKET_NAME, Key=S3_KEY, Body=output.getvalue())
    
    # Send an email with the S3 URL for the report
    report_url = "https://{}.s3.amazonaws.com/{}".format(BUCKET_NAME, S3_KEY)
    email_subject = "EC2 Uptime Report for {}".format(datetime.now().strftime('%B %Y'))
    email_body = "The EC2 uptime report for last month is ready. You can download it from: {}".format(report_url)
    
    ses_client.send_email(
        Source=EMAIL_SENDER,
        Destination={
            'ToAddresses': [EMAIL_RECIPIENT]
        },
        Message={
            'Subject': {'Data': email_subject},
            'Body': {'Text': {'Data': email_body}}
        }
    )

def lambda_handler(event, context):
    generate_uptime_report()
