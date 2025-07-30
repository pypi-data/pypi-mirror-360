import requests
from graphql import parse, print_ast
from graphql.error import GraphQLSyntaxError
from requests.exceptions import RequestException


class GraphQLExecutor:
    def __init__(self, graphql_endpoint, jwt_token=None):
        self.graphql_endpoint = graphql_endpoint
        self.jwt_token = jwt_token

    def execute(self, query: str, variables: dict = None):
        try:
            parsed_query = print_ast(parse(query))
            headers = {}
            if self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"

            request_data = {"query": parsed_query, "variables": variables}

            response = requests.post(
                self.graphql_endpoint, json=request_data, headers=headers
            )

            if not response.text:
                raise RuntimeError("Empty response received from GraphQL endpoint.")

            response_data = response.json()
            if "errors" in response_data:
                raise RuntimeError(
                    f"GraphQL request failed with errors: {response_data['errors']}"
                )

            return {"data": response_data["data"]}

        except (RequestException, GraphQLSyntaxError) as e:
            raise RuntimeError(f"Invalid GraphQL syntax: {e}")
