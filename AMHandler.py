import requests

class AMController:
	endpoint_allLibrarySongs = 'https://api.music.apple.com/v1/me/library/songs'
	
	def getAllLibrarySongs(userToken, devToken):
		response = requests.get(AMController.endpoint_allLibrarySongs,
	       	params={
				"limit": 5,
				# "sort[order]": "DESC",
				"sort": "-dateAdded"
			},
			headers={
				"Authorization": f"Bearer {devToken}",
				'Music-User-Token': userToken
			}
		)
		print(response.content)



# class AppleMusic(applemusicpy.AppleMusic):





# 	def searchLibrary(self, term, l=None, limit=None, offset=None, types=None, hints=False, os='linux'):
# 		"""
# 		Query the Apple Music API based on a search term

# 		:param term: Search term
# 		:param storefront: Apple Music store front
# 		:param l: The localization to use, specified by a language tag. Check API documentation.
# 		:param limit: The maximum amount of items to return
# 		:param offset: The index of the first item returned
# 		:param types: A list of resource types to return (e.g. songs, artists, etc.)
# 		:param hints: Include search hints
# 		:param os: Operating System being used. If search isn't working on Windows, try os='windows'.

# 		:return: The search results in JSON format
# 		"""
# 		url = self.root + 'me/library/search'
# 		if hints:
# 			url += '/hints'
# 		term = re.sub(' +', '+', term)
# 		if types:
# 			type_str = ','.join(types)
# 		else:
# 			type_str = None

# 		if os == 'linux':
# 			return self._get(url, term=term, l=l, limit=limit, offset=offset, types=type_str)
# 		elif os == 'windows':
# 			params = {
# 				'term': term,
# 				'limit': limit,
# 				'offset': offset,
# 				'types': type_str
# 			}

# 			# The params parameter in requests converts '+' to '%2b'
# 			# On some Windows computers, this breaks the API request, so generate full URL instead
# 			param_string = '?'
# 			for param, value in params.items():
# 				if value is None:
# 					continue
# 				param_string = param_string + str(param) + '=' + str(value) + '&'
# 			param_string = param_string[:len(param_string) - 1]  # This removes the last trailing '&'

# 			return self._get(url + param_string)
# 		else:
# 			return None