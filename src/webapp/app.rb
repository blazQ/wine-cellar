require 'sinatra'
require 'httparty'
require 'dotenv'
require 'date'

set :port, 8080

Dotenv.load(File.expand_path("../../../.env", __FILE__))
API_ENDPOINT = 'http://localhost:4566' # Replace with your LocalStack API endpoint

get '/' do
  query_params = {
    'room': '*'
  }
  api_id = ENV['API_ID']
  # Make a request to your LocalStack API
  response = HTTParty.get("#{API_ENDPOINT}/restapis/#{api_id}/test/_user_request_/room", query: query_params)

  if response.success?
    # Assuming your API returns JSON data
    data = JSON.parse(response.body)
    # Do something with the data and render it in your view
    erb :index, locals: { data: data }
  else
    "Error: #{response.code}"
  end
end

def color_temperature(temperature)
  temp = temperature.to_f
  if temp < 20
    return 'good-temperature'
  elsif temp < 30
    return 'warning-temperature'
  else
    return 'high-temperature'
  end
end

def color_humidity(humidity)
  humidity_val = humidity.to_i
  if humidity_val < 60
    return 'good-humidity'
  elsif humidity_val < 90
    return 'warning-humidity'
  else
    return 'high-humidity'
  end
end

def color_vibration(vibration)
  vibration_val = vibration.to_i
  if vibration_val < 3
    return 'good-vibration'
  elsif vibration_val < 7
    return 'warning-vibration'
  else
    return 'high-vibration'
  end
end

def convert_timestamp(unix_timestamp)
  unix_timestamp_n = unix_timestamp.to_i
  datetime_timestamp = Time.at(unix_timestamp_n).to_datetime
  return datetime_timestamp
end
