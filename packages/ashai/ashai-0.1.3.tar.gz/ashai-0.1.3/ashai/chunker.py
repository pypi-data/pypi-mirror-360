# # chunker.py
# from .llm_api import llm
# import uuid
# from rich import print as rprint

# class AgenticChunker:
#     def __init__(self,api_url:str,api_key:str):
#         self.api_url = api_url
#         self.api_key = api_key
#         self.chunks = {}
#         self.id_truncate_limit = 5
#         self.generate_new_metadata_ind = True
#         self.print_logging = True

#     def add_propositions(self, propositions):
#         for proposition in propositions:
#             self.add_proposition(proposition)

#     def add_proposition(self, proposition):
#         if self.print_logging:
#             rprint(f"\nAdding: '{proposition}'")

#         if not self.chunks:
#             self._create_new_chunk(proposition)
#             return

#         chunk_id = self._find_relevant_chunk(proposition)

#         # ✅ Proper fix for "No chunks"
        
#         if chunk_id:
#             self.add_proposition_to_chunk(chunk_id, proposition)
#         else:
#             self._create_new_chunk(proposition)
#     def add_proposition_to_chunk(self, chunk_id, proposition):
#         self.chunks[chunk_id]['propositions'].append(proposition)
#         if self.generate_new_metadata_ind:
#             self.chunks[chunk_id]['summary'] = self._update_chunk_summary(self.chunks[chunk_id])
#             self.chunks[chunk_id]['title'] = self._update_chunk_title(self.chunks[chunk_id])

#     def _update_chunk_summary(self, chunk):
#         system_msg = """You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
#         A new proposition was just added to one of your chunks, you should generate a very brief updated chunk title which will inform viewers what a chunk group is about.

#         A good title will say what the chunk is about.

#         You will be given a group of propositions which are in the chunk, chunk summary and the chunk title.

#         Your title should anticipate generalization. If you get a proposition about apples, generalize it to food.
#         Or month, generalize it to \"date and times\".

#         Example:
#         Input: Summary: This chunk is about dates and times that the author talks about
#         Output: Date & Times

#         Only respond with the new chunk title, nothing else."""
#         user_msg = f"Chunk's propositions:\n{chr(10).join(chunk['propositions'])}\n\nCurrent chunk summary:\n{chunk['summary']}"
#         return llm(system_msg, user_msg,self.api_url, self.api_key)

#     def _update_chunk_title(self, chunk):
#         system_msg = "You are assigning a short title to a group of related sentences based on its summary."
#         user_msg = f"Chunk's propositions:\n{chr(10).join(chunk['propositions'])}\n\nChunk summary:\n{chunk['summary']}\n\nCurrent chunk title:\n{chunk['title']}"
#         return llm(system_msg, user_msg,self.api_url, self.api_key)

#     def _get_new_chunk_summary(self, proposition):
#         system_msg = """You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
#         You should generate a very brief 1-sentence summary which will inform viewers what a chunk group is about.

#         A good summary will say what the chunk is about, and give any clarifying instructions on what to add to the chunk.

#         You will be given a proposition which will go into a new chunk. This new chunk needs a summary.

#         Your summaries should anticipate generalization. If you get a proposition about apples, generalize it to food.
#         Or month, generalize it to \"date and times\".

#         Example:
#         Input: Proposition: Greg likes to eat pizza
#         Output: This chunk contains information about the types of food Greg likes to eat.

#         Only respond with the new chunk summary, nothing else."""
#         user_msg = f"Determine the summary for the new chunk:\n{proposition}"
#         return llm(system_msg, user_msg,self.api_url, self.api_key)

#     def _get_new_chunk_title(self, summary):
#         system_msg = """You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic
#         You should generate a very brief few word chunk title which will inform viewers what a chunk group is about.

#         A good chunk title is brief but encompasses what the chunk is about

#         You will be given a summary of a chunk which needs a title

#         Your titles should anticipate generalization. If you get a proposition about apples, generalize it to food.
#         Or month, generalize it to \"date and times\".

#         Example:
#         Input: Summary: This chunk is about dates and times that the author talks about
#         Output: Date & Times

#         Only respond with the new chunk title, nothing else."""
#         user_msg = f"Determine the title of the chunk that this summary belongs to:\n{summary}"
#         return llm(system_msg, user_msg,self.api_url, self.api_key)

#     def _create_new_chunk(self, proposition):
#         new_id = str(uuid.uuid4())[:self.id_truncate_limit]
#         summary = self._get_new_chunk_summary(proposition)
#         title = self._get_new_chunk_title(summary)
#         self.chunks[new_id] = {
#             'chunk_id': new_id,
#             'propositions': [proposition],
#             'title': title,
#             'summary': summary,
#             'chunk_index': len(self.chunks)
#         }
#         if self.print_logging:
#             rprint(f"Created new chunk ({new_id}): {title}")

#     def get_chunk_outline(self):
#         return "\n\n".join([
#             f"Chunk ({chunk['chunk_id']}): {chunk['title']}\nSummary: {chunk['summary']}"
#             for chunk in self.chunks.values()
#         ])

#     # def _find_relevant_chunk(self, proposition):
#     #     outline = self.get_chunk_outline()
#     #     system_msg = """Determine whether or not the "Proposition" should belong to any of the existing chunks.

#     # A proposition should belong to a chunk if their meaning, direction, or intention are similar.
#     # The goal is to group similar propositions and chunks.

#     # If you think a proposition should be joined with a chunk, return the chunk id only (e.g., 75909).
#     # If you do not think it belongs in any chunk, return: No chunks

#     # Example:
#     # Input:
#     #     - Proposition: "Greg really likes hamburgers"
#     #     - Current Chunks:
#     #         - Chunk ID: 2n4l3d
#     #         - Chunk Name: Places in San Francisco
#     #         - Chunk Summary: Overview of the things to do with San Francisco Places

#     #         - Chunk ID: 93833k
#     #         - Chunk Name: Food Greg likes
#     #         - Chunk Summary: Lists of the food and dishes that Greg likes
#     # Output: 93833k"""

#     #     user_msg = f"Current Chunks:\n--Start--\n{outline}\n--End--\n\nEvaluate: {proposition}"
#     #     response = llm(system_msg, user_msg, self.api_url, self.api_key).strip()

#     # # Handle possible LLM formatting
#     #     if response.lower().startswith("Chunk id:"):
#     #      response = response.split(":", 1)[1].strip()

#     #     return response if response in self.chunks or response.lower() == "no chunks" else None

#     def _find_relevant_chunk(self, proposition):
#         outline = self.get_chunk_outline()
#         system_msg = """You must return ONLY the chunk ID from the list below if the proposition belongs to any of them.
# Return "No chunks" if none match. Do NOT add any prefix like 'Chunk ID:'.

# Example:
# - Return: 123ab
# - Or: No chunks"""
    
#         user_msg = f"Current Chunks:\n--Start--\n{outline}\n--End--\n\nEvaluate: {proposition}"
#         response = llm(system_msg, user_msg, self.api_url, self.api_key).strip()

#     # ✅ Strip and clean the response
#         if ":" in response:  # If LLM still replies like "Chunk ID: xxx"
#             response = response.split(":")[-1].strip()

#         if response.lower() == "no chunks":
#             return None

#         if response in self.chunks:
#             return response
#         else:
#         # Log unrecognized chunk ID and fall back safely
#             if self.print_logging:
#                 rprint(f"[red]Warning: Returned chunk ID '{response}' not found. Creating new chunk.[/red]")
#             return None


#     def get_chunks(self, get_type='dict'):
#         if get_type == 'dict':
#             return self.chunks
#         elif get_type == 'list_of_strings':
#             return [" ".join(chunk['propositions']) for chunk in self.chunks.values()]

#     def pretty_print_chunks(self):
#         rprint(f"\n[bold yellow]Total Chunks:[/bold yellow] {len(self.chunks)}\n")
#         for chunk in self.chunks.values():
#             rprint(f"[bold blue]Chunk #{chunk['chunk_index']}[/bold blue] - [green]{chunk['title']}[/green]")
#             rprint(f"Summary: {chunk['summary']}")
#             for prop in chunk['propositions']:
#                 rprint(f"  - {prop}")
#             rprint("\n")





# chunker.py
from .llm_api import llm
import uuid
from rich import print as rprint

class AgenticChunker:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.chunks = {}
        self.id_truncate_limit = 5
        self.generate_new_metadata_ind = True
        self.print_logging = True

    def add_propositions(self, propositions):
        for proposition in propositions:
            self.add_proposition(proposition)

    def add_proposition(self, proposition):
        if self.print_logging:
            rprint(f"\nAdding: '{proposition}'")

        # If no chunks exist yet, create the first one
        if not self.chunks:
            self._create_new_chunk(proposition)
            return

        chunk_id = self._find_relevant_chunk(proposition)

        # Use only valid chunk IDs; create new if None
        if chunk_id and chunk_id in self.chunks:
            self.add_proposition_to_chunk(chunk_id, proposition)
        else:
            self._create_new_chunk(proposition)

    def add_proposition_to_chunk(self, chunk_id, proposition):
        self.chunks[chunk_id]['propositions'].append(proposition)
        if self.generate_new_metadata_ind:
            self.chunks[chunk_id]['summary'] = self._update_chunk_summary(self.chunks[chunk_id])
            self.chunks[chunk_id]['title'] = self._update_chunk_title(self.chunks[chunk_id])

    def _update_chunk_summary(self, chunk):
        system_msg = (
            "You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic. "
            "A new proposition was just added to one of your chunks; generate a very brief updated summary describing the chunk contents."
        )
        user_msg = f"Propositions:\n{chr(10).join(chunk['propositions'])}\n\nCurrent summary:\n{chunk['summary']}"
        return llm(system_msg, user_msg, self.api_url, self.api_key)

    def _update_chunk_title(self, chunk):
        system_msg = (
            "You are assigning a short title to a group of related propositions based on its summary. "
            "Generate a concise title."
        )
        user_msg = (
            f"Propositions:\n{chr(10).join(chunk['propositions'])}\n\n"
            f"Summary:\n{chunk['summary']}\n\n"
            f"Current title:\n{chunk['title']}"
        )
        return llm(system_msg, user_msg, self.api_url, self.api_key)

    def _get_new_chunk_summary(self, proposition):
        system_msg = (
            "You are the steward of a group of chunks which represent groups of sentences that talk about a similar topic. "
            "Generate a brief, 1-sentence summary for this chunk."
        )
        user_msg = f"Determine the summary for the new chunk:\n{proposition}"
        return llm(system_msg, user_msg, self.api_url, self.api_key)

    def _get_new_chunk_title(self, summary):
        system_msg = (
            "You should generate a very brief (3–5 words) title to inform viewers what a chunk group is about."
        )
        user_msg = f"Determine the title for this summary:\n{summary}"
        return llm(system_msg, user_msg, self.api_url, self.api_key)

    def _create_new_chunk(self, proposition):
        new_id = str(uuid.uuid4())[:self.id_truncate_limit]
        summary = self._get_new_chunk_summary(proposition)
        title = self._get_new_chunk_title(summary)
        self.chunks[new_id] = {
            'chunk_id': new_id,
            'propositions': [proposition],
            'title': title,
            'summary': summary,
            'chunk_index': len(self.chunks)
        }
        if self.print_logging:
            rprint(f"Created new chunk ({new_id}): {title}")

    def get_chunk_outline(self):
        return "\n\n".join([
            f"Chunk ({c['chunk_id']}): {c['title']}\nSummary: {c['summary']}"
            for c in self.chunks.values()
        ])

    def _find_relevant_chunk(self, proposition):
        outline = self.get_chunk_outline()
        system_msg = (
            "You must return ONLY the chunk ID if the proposition belongs to an existing chunk. "
            "Return exactly 'No chunks' if it does not. Do NOT add any prefix."
        )
        user_msg = f"Current Chunks:\n--Start--\n{outline}\n--End--\n\nEvaluate: {proposition}"
        response = llm(system_msg, user_msg, self.api_url, self.api_key).strip()

        # Clean response: strip any prefix
        if ':' in response:
            response = response.split(':')[-1].strip()

        # Interpret 'no chunks'
        if response.lower() == 'no chunks':
            return None

        # Only return valid IDs
        if response in self.chunks:
            return response
        if self.print_logging:
            rprint(f"[red]Warning: Returned chunk ID '{response}' not found.\nCreating new chunk instead.[/red]")
        return None

    def get_chunks(self, get_type='dict'):
        if get_type == 'dict':
            return self.chunks
        elif get_type == 'list_of_strings':
            return [" ".join(c['propositions']) for c in self.chunks.values()]

    def pretty_print_chunks(self):
        rprint(f"\n[bold yellow]Total Chunks:[/bold yellow] {len(self.chunks)}\n")
        for c in self.chunks.values():
            rprint(f"[bold blue]Chunk #{c['chunk_index']}[/bold blue] - [green]{c['title']}[/green]")
            rprint(f"Summary: {c['summary']}")
            for p in c['propositions']:
                rprint(f"  - {p}")
            rprint("\n")
