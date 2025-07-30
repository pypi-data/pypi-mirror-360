import requests
import json
import pandas as pd

class ContentChecker:

  def __init__(self, key, data=None, resource=None, threshold=0.5, contract_id=None):
      
      self.contract_id = contract_id
      self.threshold = threshold
      self.resource = resource
      self.data = data
      self.key = key
      
      if contract_id == None:
          self.url = 'https://http.msging.net/commands'
      else:
          self.url = f'https://{contract_id}.http.msging.net/commands'

      self.header = {
            'content-type': 'application/json',
            'Authorization': self.key
            }
      """  
        if isinstance(data, None) == False:
          if isinstance(data, pd.DataFrame) == False:
            print(f'Ao invés de "{data}", favor inserir um DataFrame. A coluna com o texto deve ter o cabeçalho com o nome "Text".')
          else:
            pass

        if isinstance(resource, None) == False:
          if isinstance(resource, str) == False:
            print(f'Ao invés de "{data}", favor inserir o nome do seu recurso.')
          else:
            pass
      """

  def identityanalysis(self):
    try:
      df = self.data[['Text', 'Intention', 'Entities', 'Score']]
      ent = []

      for i in range(len(df)):
        if df.Entities[i] != '[]':
          ent.append(pd.json_normalize(json.loads(df.Entities[i])).value.tolist())
        else:
          ent.append('')
      
      df.loc[:, 'Content'] = [self.test(model='n', intention=df.Intention[x], entities=ent[x]) for x in range(len(df.Entities))]
      
      #df = df.sort_values(by='Content',ascending=False)
      df = self.check_threshold(df)
      return(df)
    
    except KeyError: 
      print("O seu dataframe deve conter as seguintes colunas ['Text', 'Intention', 'Entities', 'Score']. Você pode obtê-las pela tabela vwidentityanalysis.")


  def sentences(self, resource=None):

    if isinstance(resource,pd.DataFrame):
      df = resource
    else:
      df = self.data
    
      if any(col in ['intentions', 'intent', 'intention', 'score', 'entities', 'entity'] for col in self.data.columns.str.lower()):
        print("Ops, o método sentences não é melhor método para a sua operação. Que tal utilizar o identityanalysis?")

      else:
        pass
    
    df = pd.DataFrame([self.test(model='y',text=t) for t in df.Text])
    df = df[['text','intentions','entities']]
    df['Score'] = df.intentions.apply(lambda s: s[0]['score'])
    df.intentions = df.intentions.apply(lambda i: i[0]['id'])
    df.columns = ['Text', 'Intention', 'Entities', 'Score']
    
    #ent = [pd.json_normalize(df.Entities[i]).value.tolist() if df.Entities[i] != '[]' else '' for i in range(len(df.Text))]

    ent = []
    for i in range(len(df.Text)):
        try:
          ent.append(pd.json_normalize(df.Entities[i]).value.tolist())
        except AttributeError:
          ent.append('')

    df.loc[:, 'Content'] = [self.test(model='n', intention=df.Intention[x], entities=ent[x]) for x in range(len(df.Entities))]
        
    return(self.check_threshold(df))

  def byresource(self):

    body ={  
            "id": "{{$guid}}",
            "method": "get",
            "uri": f"/resources/{self.resource}"
          }        
    
    
    r = requests.post(self.url, json=body,headers=self.header).json()
    
    try:
      df = pd.DataFrame({'Text':r['resource'].split(',')})
      return(self.sentences(df))
    except KeyError:
      if r['code'] == 13:
        print("Verifique se o contract_id e/ou a key estão corretos.")
      elif r['code'] == 67:
        print("o recurso teste-modelo não foi encontrado, confira a existência e o nome do seu recurso.")
      else:
        print(f"Ops, algo de errado aconteceu. - {r['code']}")


  def test(self, model, text=None, intention=None, entities=None):

    if model == 'y':

      body =  {
                "id": "{{$guid}}",
                "to": "postmaster@ai.msging.net",
                "method": "set",
                "uri": "/analysis",
                "type": "application/vnd.iris.ai.analysis-request+json",
                "resource": {
                  "text":f"{text}"
                }
              }
      
      tr = requests.post(self.url, json=body,headers=self.header).json()

      result = tr['resource']

    elif model == 'n':
        if isinstance(entities, str):
          result = self.test_content(intention,[entities])
        elif isinstance(entities, list):
          result = self.test_content(intention,entities)

    else:
      print('O parâmetro model deve ter o valor de y ou n.')

    return(result)

  def test_content(self, intention, entities):

    if isinstance(entities, str):
        if entities == '' or entities == '['']' or entities == ['']:
          entities = []
        else:
          entities = [entities]
    elif isinstance(entities, list):
        if entities == '' or entities == '['']' or entities == ['']:
          entities = []
        else:
          pass

    body =  {
              "id": "46544651",
              "to": "postmaster@ai.msging.net",
              "method": "set",
              "uri": "/content/analysis",
              "resource": {
                "intent": intention,
                "entities":entities,
                "minEntityMatch":1
                },
              "type": "application/vnd.iris.ai.content-combination+json"
            }
    try:        
      r = requests.post(self.url, json=body,headers=self.header).json()['resource']['result']['content']
    except KeyError:
      r = 'no_answer'
    return(r)
  
  def check_threshold(self,df):
    
    df = df.reset_index()
    df.Content = df.Content.astype(str)
    df.Score = df.Score.astype(float)

    atention = []
    delivered = []

    for i in range(len(df)):

      if df.Score.iloc[i] <= self.threshold and df.Content.iloc[i] == "no_answer":
        atention.append('model')
        delivered.append('n')
      elif df.Score.iloc[i] <= self.threshold and df.Content.iloc[i] != "no_answer":
        atention.append('refine')
        delivered.append('n')
      elif df.Score.iloc[i] >= self.threshold and df.Content.iloc[i] != "no_answer":
        atention.append('valid')
        delivered.append('y')
      elif df.Score.iloc[i] >= self.threshold and df.Content.iloc[i] == "no_answer":
        delivered.append('n')
        if df.Entities.iloc[i] != '[]':
          atention.append('content | entity in the combination')
        else:
          atention.append('content | entity in the model')
      else:
        delivered.append('x')
        atention.append('x')
    
    df['Delivered'] = delivered  
    df['Atention'] = atention
   
    return(df)
    
    

      
