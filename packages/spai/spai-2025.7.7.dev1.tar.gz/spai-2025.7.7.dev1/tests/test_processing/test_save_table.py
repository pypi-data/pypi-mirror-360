from unittest import mock
import pandas as pd
from spai.spai.processing.save_table import save_table

# Test save_table function
def test_save_table():
    
    data =[1,2]
    columns = ["column1","column2"]
    date = pd.Timestamp('2019-06-02').date()
    test_df = pd.DataFrame([data],  columns=columns,  index=[date])
    
    storage = mock.Mock()
    storage.list.return_value = []
    storage.create.return_value = "path"
    result = save_table(data=data, columns=columns, table_name="table_name", date=date, storage=storage)
    storage.create.assert_called_once()
    assert result.equals(test_df)