def bagged_model(models,X):
    predictions=[]
    for i in X:
        pred = []
        for model in models:
            pred.append(model.predict([i])[0])
        if sum(pred) / len(models)>0.5:
            predictions.append(1)
        else:
            predictions.append(0)

    return predictions