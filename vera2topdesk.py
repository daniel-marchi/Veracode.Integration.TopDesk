import json
import http.client
import base64

# region FUNCTIONS: SETUP

def setup_env_variables():
    #rootdir = "/home/vsts/work/1/s/"


    return {
        "azure": {
            "workspace": {
                "root": rootdir
            }
        },
        "topdesk": {
            "auth": {
                "user": "???", #Usuário para integração TopDesk
                "key": "???" #Senha para integração TopDesk
            },
            "payloads": {
                # "sast": f"{rootdir}/topdesk/pipeline.json",
                "sast": f"{rootdir}/topdesk/resumeSAST.json",
                "sca": f"{rootdir}/topdesk/resumeSCA.json",
                "incident": f"{rootdir}/topdesk/payloadIncidente.json",
            },
            "url": "petros-test.topdesk.net"
        },
        "veracode": {
            "results": {
                # "sast": f"{rootdir}/veracode/pipeline.json",
                "sast": f"{rootdir}/veracode/resultsSAST.json",
                "sca": f"{rootdir}/veracode/resultsSCA.json",
            }
        },
    }

def setup(env_variables, requests):
    return {
        "env": env_variables,
        "requests": requests
    }

def setup_requests():
    return {
        "topdesk": {
            "incident": {
                "request": "",  # Titulo
                "caller": {
                    "id": "349ed95f-3d1f-4905-a6f8-38e8acb80df6",
                    "phoneNumber": "",
                    "branch": {
                        "id": "1c36847a-dde9-48d6-bc7d-230a30791754",
                        "clientReferenceNumber": ""
                    }
                },
                "briefDescription": "",  # Descricao
                "callType": {
                    "id": "b46bd95d-1b4b-5667-bf6a-86531696c8cc"
                },
                #"object": null,  # Obrigatório
                "impact": {
                    "id": "8571eab3-83e8-53cc-9806-c4cc92e4add3"
                },
                "urgency": {
                    "id": "894b5cf8-72e5-4e26-9acd-5a9b13234a38"
                },
                "priority": {
                    "id": "cca45fc4-d6d5-439b-9ae4-beeed1a01c91"
                },
                "duration": {
                    "id": "ae667716-1d73-422d-a410-742e70f996c4"
                },
                #"targetDate": "2023-09-27T13:07:00.000+0000",
                #"operator": null,  # Obrigatório
                #"operatorGroup": null,  # Obrigatório
                "processingStatus": {
                    "id": "a3e2ad64-16e2-4fe3-9c66-9e50ad9c4d69"
                }
            }
        }
    }

def setup_topdesk_results():
    return {
        "success":True,
        "sast": {
            "success":True,
            "results":[]
            },
        "sca": {
            "success":True,
            "results":[]
            }
        }
# endregion

# region FUNCTIONS: Main

def main():
    print(f'Integração Veracode e TopDesk')
    print(f'------------------------------------------')

    print(f'1/5 Carregando Variáveis...\n')
    env_variables = setup_env_variables()
    default_requests = setup_requests()
    setup_data = setup(env_variables, default_requests)
    topdesk_results =setup_topdesk_results()

    print(f'setup_data\n{setup_data}\n')
    print(f'1/5 Carregando Variáveis... OK!')
    print(f'------------------------------------------')

    print(f'2/5 Veracode: Carregando Resultados SAST...')
    result_sast = read_json_file(env_variables["veracode"]["results"]["sast"])
    parsed_sast = vera_parse_sast(result_sast)
    write_json_file(env_variables["topdesk"]["payloads"]["sast"], parsed_sast)

    print(f'parsed_sast\n{parsed_sast}\n')
    print(f'2/5 Veracode: Carregando Resultados SAST...Ok')
    print(f'------------------------------------------')

    print(f'3/5 Veracode: Carregando Resultados SCA...')
    result_sca = read_json_file(env_variables["veracode"]["results"]["sca"])
    parsed_sca = vera_parse_sca(result_sca)
    write_json_file(env_variables["topdesk"]["payloads"]["sca"], parsed_sca)

    print(f'parsed_sca\n{parsed_sca}\n')
    print(f'3/5 Veracode: Carregando Resultados SCA...Ok')
    print(f'------------------------------------------')

    print(f'4/5 Topdesk: Criando Incidentes SAST...')
    resume_sast = read_json_file(env_variables["topdesk"]["payloads"]["sast"])

    for index, item in enumerate(resume_sast):
        payload=topdesk_create_payload(default_requests["topdesk"]["incident"], item)
        response = topdesk_send_request(env_variables["topdesk"]["url"]
                                        , payload
                                        , env_variables["topdesk"]["auth"]["user"]
                                        , env_variables["topdesk"]["auth"]["key"])

        result = http_response_handle(response,payload,index)
        topdesk_results["sast"]["results"].append(result)

        if not result:
            topdesk_results["success"] = False

        print(f'o==|============> ****** (Oo) --------')
        print(f'# {index+1}/{len(resume_sast)} - Resultado do request:\n{result}')

    print(f'topdesk_results\n{topdesk_results}\n')
    print(f'4/5 Topdesk: Criando Incidentes SAST...OK!')
    print(f'------------------------------------------')

    print(f'5/5 Topdesk: Criando Incidentes SCA...')
    resume_sca = read_json_file(env_variables["topdesk"]["payloads"]["sca"])

    for index, item in enumerate(resume_sca):
        payload = topdesk_create_payload(default_requests["topdesk"]["incident"], item)
        response = topdesk_send_request(env_variables["topdesk"]["url"]
                                        , payload
                                        , env_variables["topdesk"]["auth"]["user"]
                                        , env_variables["topdesk"]["auth"]["key"])

        result = http_response_handle(response,payload,index)
        topdesk_results["sca"]["results"].append(result)

        if not result:
            topdesk_results["success"] = False

        print(f'o==|============> ****** (Oo) --------')
        print(f'# {index+1}/{len(resume_sca)} - Resultado do request:\n{result}')

    print(f'topdesk_results\n{topdesk_results}\n')
    print(f'5/5 Topdesk: Criando Incidentes SCA...OK!')
    print(f'------------------------------------------')

    print(f'sucesso_integração:\n{topdesk_results["success"]}\n')
    print(f'\n\nFIM')

def read_json_file(path):
    with open(path, 'r') as file:
        return json.load(file)

def http_response_handle(response, request, index=0):
    success = False
    incident_number="erro"

    if 200 <= response.status < 300:
        content = json.loads(response.read().decode())
        incident_number=content["number"]
        success=True
        message = f"HTTP {response.status}: Sucesso!"
    else:
        message = f"HTTP {response.status}: Erro: {response.status}"

    return {
        "incident_number": incident_number,
        "index": index,
        "message": message,
        "request": request,
        "success": success,
    }

def write_json_file(path, content):
    with open(path, 'w') as output_file:
        json.dump(content, output_file, indent=4)

# endregion

# region FUNCTIONS: Topdesk

def topdesk_create_payload(payload, content):
    payload["request"]=content["title"]
    payload["briefDescription"]=content["description"]
    return payload

def topdesk_send_request(url, payload, usr, passwd):
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{usr}:{passwd}".encode()).decode()}',
        'Content-Type': 'application/json'
    }

    conn = http.client.HTTPSConnection(url)
    conn.request('POST', '/tas/api/incidents', json.dumps(payload), headers)

    return conn.getresponse()

# endregion

# region FUNCTIONS: Veracode

def vera_severity(id):
    sev = 'error'
    match id:
        case 1:
            sev='very low (1)'
        case 2:
            sev='low (2)'
        case 3:
            sev='medium (3)'
        case 4:
            sev='high (4)'
        case 5:
            sev='very high (5)'
    return sev

def vera_parse_sast(data):
    results = []
    for finding in data['findings']:
        title = finding['title']
        issue_id = finding['issue_id']
        cwe_id = finding['cwe_id']
        severity = vera_severity(finding['severity'])
        issue_type = finding['issue_type']
        display_text = finding['display_text']

        results.append({
            "title": f'{issue_id} - CWE-{cwe_id} - {issue_type}',
            "description": "descrição de pedido"
            })
    return results

def vera_parse_sca(data):
    results = []
    for vuln in data['records'][0]['vulnerabilities']:
        results.append({
            "title": f'CVE-{vuln["cve"]}: {vuln["title"]}',
            "description": f'<a href="{vuln["_links"]["html"]}">{vuln["_links"]["html"]}</a>'
            })
    return results

# endregion

main()
