import { callPython, bridgeReturn, registerFunction } from './pythonBridge_browser';
import { jupyter_prompt } from "./prompts"


export class VoittaToolRouter {
  public prompt = jupyter_prompt;
  public tools = [];

  constructor() {

  }

  public get_prompt() {
    return this.prompt;
  }
  public get_tools() {
    // this assumes antropic -> openai
    return convertToOpenAPI(this.tools);
  }
  public intraspect() {

    console.log("-------- Intraspection called ------")
    return ({ "prompt": this.get_prompt(), "tools": this.get_tools() });
  }
}











/* TODO: move this into a different file */




/**
 * Interface definitions for function arguments
 */
interface ArgumentDefinition {
  type: string;
  name: string;
  description?: string;
  required?: boolean;
  default?: any;
}

/**
 * Interface definition for the function structure
 */
interface FunctionDefinition {
  name: string;
  description: string;
  arguments: Record<string, ArgumentDefinition>;
}

/**
 * Interface for the OpenAPI schema output
 */
interface OpenAPISchema {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  paths: Record<string, Record<string, any>>;
  components: {
    schemas: Record<string, any>;
  };
}

/**
 * Converts a type from your custom format to OpenAPI schema type
 */
function convertType(type: string): string {
  const typeMap: Record<string, string> = {
    'str': 'string',
    'int': 'integer',
    'float': 'number',
    'bool': 'boolean',
    'object': 'object',
    'array': 'array'
  };

  return typeMap[type] || type;
}

/**
 * Creates a Pascal case version of a string (for FastAPI schema naming)
 * @param str Input string
 * @returns Pascal case string
 */
function toPascalCase(str: string): string {
  return str
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('');
}

/**
 * Converts function definitions to OpenAPI specification in FastAPI format
 * @param functions Array of function definitions
 * @param apiTitle Title for the API
 * @param apiVersion Version for the API
 * @returns OpenAPI specification as a JavaScript object
 */
function convertToOpenAPI(
  functions: FunctionDefinition[],
  apiTitle: string = "FastAPI",
  apiVersion: string = "0.1.0"
): OpenAPISchema {
  const openapi: OpenAPISchema = {
    openapi: "3.1.0",
    info: {
      title: apiTitle,
      version: apiVersion,
    },
    paths: {
      "/__prompt__": {
        "get": {
          "summary": "Prompt",
          "operationId": "prompt___prompt___get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {}
                }
              }
            }
          }
        }
      }
    },
    components: {
      schemas: {
        "HTTPValidationError": {
          "properties": {
            "detail": {
              "items": {
                "$ref": "#/components/schemas/ValidationError"
              },
              "type": "array",
              "title": "Detail"
            }
          },
          "type": "object",
          "title": "HTTPValidationError"
        },
        "ValidationError": {
          "properties": {
            "loc": {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  }
                ]
              },
              "type": "array",
              "title": "Location"
            },
            "msg": {
              "type": "string",
              "title": "Message"
            },
            "type": {
              "type": "string",
              "title": "Error Type"
            }
          },
          "type": "object",
          "required": ["loc", "msg", "type"],
          "title": "ValidationError"
        }
      }
    }
  };

  functions.forEach(func => {
    // Convert function to FastAPI path endpoint format
    const path = `/${func.name}`;
    const operationId = `${func.name}_${func.name}_post`;
    const bodySchemaName = `Body_${func.name}_${func.name}_post`;

    // Create request body schema for the components section
    const requestBodySchema: any = {
      properties: {},
      type: "object",
      required: [],
      title: bodySchemaName
    };

    // Add parameters to request body schema
    Object.entries(func.arguments).forEach(([argName, argDetails]) => {
      requestBodySchema.properties[argName] = {
        type: convertType(argDetails.type),
        title: toPascalCase(argName),
        description: argDetails.name
      };

      // Add default value if available
      if (argDetails.default !== undefined) {
        requestBodySchema.properties[argName].default = argDetails.default;
      }

      // Add to required list if marked as required or by default
      if (argDetails.required !== false) {
        requestBodySchema.required.push(argName);
      }
    });

    // Add schema to components
    openapi.components.schemas[bodySchemaName] = requestBodySchema;

    // Add the path operation
    openapi.paths[path] = {
      post: {
        summary: toPascalCase(func.name.split('_').join(' ')),
        description: func.description,
        operationId: operationId,
        parameters: [
          {
            name: "authorization",
            in: "header",
            required: false,
            schema: {
              type: "string",
              title: "Authorization"
            }
          },
          {
            name: "oauthtoken",
            in: "header",
            required: false,
            schema: {
              type: "string",
              title: "Oauthtoken"
            }
          }
        ],
        requestBody: {
          required: true,
          content: {
            "application/x-www-form-urlencoded": {
              schema: {
                "$ref": `#/components/schemas/${bodySchemaName}`
              }
            }
          }
        },
        responses: {
          "200": {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {}
              }
            }
          },
          "422": {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        },
        "x-CPM": "1.0"
      }
    };
  });

  return openapi;
}