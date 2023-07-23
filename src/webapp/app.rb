require 'sinatra'
require 'httparty'
require 'dotenv'


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