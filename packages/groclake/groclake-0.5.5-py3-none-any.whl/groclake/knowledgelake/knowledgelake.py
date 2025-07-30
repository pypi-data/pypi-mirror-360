from ..utillake import Utillake
from groclake.vectorlake import Vectorlake
from groclake.datalake import Datalake
from groclake.modellake import Modellake

class Knowledgelake:
    def __init__(self):
        self.utillake = Utillake()
        self.knowledgelake_id = None
        self.params = {}
        self.vector = Vectorlake()
        self.datalake = Datalake()
        self.model = Modellake()

    def push(self, product_object):
        """Processes multiple documents (URLs or local files) and pushes their generated vectors sequentially."""
        try:
            document_list = product_object.get("document_data")
            document_source = product_object.get("document_source")
            # Ensure document_data is a list (convert single entry to a list if needed)
            if not isinstance(document_list, list):
                document_list = [document_list]

            results = []

            for doc in document_list:
                single_payload = {
                    "document_type": product_object["document_type"],
                    "document_source": document_source,
                    "document_data": doc
                }
                payload = self.utillake.call_knowledgelake_payload(single_payload, self)
                document_data = payload.get("document_data")
                document_type = payload.get("document_type")
                vectorlake_id = payload.get("knowledgelake_id")

                if not all([document_data, document_type, vectorlake_id]):
                    results.append({"error": "Missing required fields.", "document": doc})
                    continue  # Skip this document and move to the next one
                
                if document_type == "notion" and document_source == "url":    
                    markdown_content = self.datalake.fetch_notion_data(doc)
                # Generate Markdown for both URL & Local
                elif document_type == "google_docs" and document_source == "url":
                    markdown_content = self.datalake.extract_google_doc(doc)
                    
                elif document_type == "google_sheets" and document_source == "url":
                    markdown_content = self.datalake.extract_google_sheet(doc)
                    
                else:
                    markdown_content = self.datalake.generate_markdown(payload)
                if not markdown_content:    
                    results.append({"error": "Failed to generate markdown.", "document": doc})
                    continue

                vector_fetch = self.vector.generate(markdown_content)
                generate_vector = vector_fetch.get("vector")

                if not generate_vector:
                    results.append({"error": "Failed to generate vector.", "document": doc})
                    continue

                push_payload = {
                    "vector": generate_vector,
                    "document_text": markdown_content,
                    "vector_type": "text",
                    "vectorlake_id": vectorlake_id
                }
                vector_push = self.vector.push(push_payload)
                vector_id = vector_push.get("vector_id")

                if vector_id:
                    results.append({"message": "Document processed and vector pushed successfully.", "document": doc})
                else:
                    results.append({"error": "Failed to push vector.", "document": doc})

            return results  # Returns a list of results for all documents

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500


    def create(self, payload=None):
        """Creates a new vector lake entry."""
        try:
            vector_create = self.vector.create()
            vectorlake_id = vector_create.get('vectorlake_id')

            if vectorlake_id:
                self.knowledgelake_id = vectorlake_id
                return {'knowledgelake_id': vectorlake_id}
            else:
                return {"error": "Failed to create vector lake entry."}, 500

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def search(self, query):
        """Performs a search operation based on the query."""
        try:
            payload = self.utillake.call_knowledgelake_payload({'query': query}, self)
            vectorlake_id = payload.get("knowledgelake_id")
            if not vectorlake_id:
                return {"error": "Vector lake ID not found."}, 400

            vector_fetch = self.vector.generate(query)
            generate_vector = vector_fetch.get("vector")

            if not generate_vector:
                return {"error": "Failed to generate vector."}, 500

            search_payload = {
                "vector": generate_vector,
                "query": query,
                "vector_type": "text",
                "vectorlake_id": vectorlake_id
            }
            vector_search = self.vector.search(search_payload)
            results = vector_search.get("results", [])

            if not results:
                return {"message": "No results found."}

            first_vector_document = results[0].get("vector_document")

            payload = {
                "messages": [
                    {"role": "system", "content": first_vector_document},
                    {"role": "user", "content": query}
                ]
            }
            chat_response = self.model.chat_complete(payload=payload)
            return chat_response

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

