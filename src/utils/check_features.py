import pickle

with open('../models/feature_names.pkl', 'rb') as f:
    features = pickle.load(f)

print('Model expects', len(features), 'features')
print('First 15 features:')
for i, feat in enumerate(features[:15]):
    print(f'  {i+1}. {feat}')

print('\nLast 15 features:')
for i, feat in enumerate(features[-15:]):
    print(f'  {len(features)-14+i}. {feat}')