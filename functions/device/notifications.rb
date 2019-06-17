require 'aws-sdk'
require 'json'

# This function is triggered when an element is added to the queue
def publish(event:, context:)
  begin
    iot = Aws::IoT::Client.new(region: 'ap-northeast-1')

    endpoint = "https://#{iot.describe_endpoint.endpoint_address}"
    puts "Publish on #{endpoint}"

    client = Aws::IoTDataPlane::Client.new({
      region: 'ap-northeast-1',
      endpoint: endpoint
    })

    # 'event' may contains multiple records
    event['Records'].each do |record|
      puts "message: #{record['body']}"

      payload = {
        message: record['body']
      }.to_json

      resp = client.publish({
        topic: ENV['TOPIC'],
        qos: 0,
        payload: payload
      })
    end

    {}
  rescue StandardError => e
    puts e.message
    puts e.backtrace.inspect
    {}
  end
end
