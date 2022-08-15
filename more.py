def calc_metrics(the_df, threshold=0.5, the_index=['baseline'], proba_col='Naive.Logistic_predict_probability', response_col='Naive.Logistic_predict_response', append_df=pd.DataFrame()):
    my_dict = {}
    if not isinstance(the_index,list):
        the_index = [the_index]
    TP = sum((the_df['target']==1)&(the_df[proba_col]>=threshold))
    TN = sum((the_df['target']==0)&(the_df[proba_col]<threshold))
    FP = sum((the_df['target']==0)&(the_df[proba_col]>=threshold))
    FN = sum((the_df['target']==1)&(the_df[proba_col]<threshold))
    my_dict['distribution'] = df['target'].mean()
    my_dict['recall'] = TP/(TP+FN)
    my_dict['precision'] = TP/(TP+FP)
    my_dict['f1'] = (2*my_dict['recall']*my_dict['precision'])/(my_dict['recall']+my_dict['precision'])
    my_dict['lift'] = my_dict['precision']/my_dict['distribution']
    my_dict['diff1'] = TP-FP
    my_dict['diff0'] = TN-FN
    my_dict['TP'] = TP
    my_dict['FP'] = FP
    my_dict['TN'] = TN
    my_dict['FN'] = FN
    res = pd.DataFrame(my_dict, index=the_index)
    if len(append_df)>0:
        return pd.concat([append_df, res],axis=0)
    return res

calc_metrics(df, threshold=0.78)
