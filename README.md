## Steps to run the project:

1. Download Grakn Core 1.8.4 from 'https://grakn.ai/download#core' and Grakn Workbase from 'https://grakn.ai/download#workbase' and unzip them.

2. Place the 'invoice_graph' folder with the files present inside, in the unzipped Grakn-Core folder.

3. On the terminal, cd into the unzipped folder of Grakn-Core and start the Grakn server using './grakn server start'.

4. Load the schema into a keyspace 'invoice_rep' using : './grakn console --keyspace invoice_rep --file invoice_graph/schema_invoice.gql'.

5. After loading the schema, run the migrate.py code using 'python3 migrate.py'.

6. After the graql data is inserted, go into the unzipped Grakn Workbase folder and open the 'grakn-workbase'.

7. With port number '48555', click 'Connect'.

8. After entering workbase, select the 'invoice_rep' keyspace in the top right corner.

9. Open the type panel which is to the left of the editor, select 'relations', and 'includes'. Alternatively, you can type 'match $x isa includes; get;' in the editor.

10. Click on the run button to the right of the editor, and the knowledge graph is visualized. You can tinker with the graph by moving components around, and with the attributes and colours through the gear icon on the right panel.

11. After use, you can stop the Grakn server using '/grakn server stop'.


