require 'json'

def notifhome(event:, context:)
  begin
    puts "Received Request: #{event}"
    { statusCode: 200, body: JSON.generate({:msg => "Notifhome #{event['body']}"}) }
  rescue StandardError => e
    puts e.message
    puts e.backtrace.inspect
    { statusCode: 400, body: JSON.generate({:msg => "Bad request, please POST a request body!"}) }
  end
end

