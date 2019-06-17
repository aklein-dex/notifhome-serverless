require 'aws-sdk'
require 'json'

# Add a notification into the queue
def create(event:, context:)
  begin
    print_event_info(event)
    params = JSON.parse(event['body'])

    raise 'Missing required parameter \'message\'' if params['message'] == nil

    sqs = Aws::SQS::Client.new(region: 'ap-northeast-1')
    sqs.send_message(queue_url: ENV['SQS_URL'], message_body: params['message'])

    { statusCode: 200 }
  rescue TypeError => e
    puts e.message
    { statusCode: 400, body: JSON.generate({ msg: 'Error: missing body parameter \'message\'' }) }
  rescue JSON::ParserError => e
    puts e.message
    { statusCode: 400, body: JSON.generate({ msg: 'Error: unable to parse request parameters' }) }
  rescue StandardError => e
    puts e.message
    puts e.backtrace.inspect
    { statusCode: 400, body: JSON.generate({ msg: e.message }) }
  end
end

# Print event information
def print_event_info(event)
  arn = event['requestContext']['identity']['userArn']
  user = arn.split('/')[1]
  puts "Received Request [#{event['httpMethod']}] #{event['path']} from #{user}: #{event['body']}"
end