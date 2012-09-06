package com.example;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import com.google.api.client.auth.oauth2.Credential;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeFlow;
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import com.google.api.client.googleapis.auth.oauth2.GoogleTokenResponse;
import com.google.api.client.http.FileContent;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.jackson.JacksonFactory;
import com.google.api.services.drive.Drive;
import com.google.api.services.drive.DriveScopes;
import com.google.api.services.drive.model.File;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;


public class MyActivity extends Activity {

	private static String CLIENT_ID = "608321796466";
	private static String CLIENT_SECRET = "2vC58uxpnVDnoId03VLeNIYH";

	private static String REDIRECT_URI = "http://localhost";
	private Drive drive;

	/**
	 * Called when the activity is first created.
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		((Button)findViewById(R.id.main__open_book_button)).setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {

				GoogleAuthorizationCodeFlow flow = PassRepoGoogleAuthorizationCodeFlow.getInstance(context);

				Credential cred = null;
				try {
					cred = flow.loadCredential("");
				} catch(IOException e) {
					e.printStackTrace();
				}

				HttpTransport ht = new NetHttpTransport();
				JacksonFactory jsonF = new JacksonFactory();
				drive = new Drive.Builder(ht, jsonF, cred).build();




				HttpTransport httpTransport = new NetHttpTransport();
				JsonFactory jsonFactory = new JacksonFactory();

				try {
					cred = PassRepoGoogleAuthorizationCodeFlow.getInstance(context.getApplicationContext()).loadCredential("");
				} catch(IOException e) {
					throw new RuntimeException(e);
				}


				GoogleAuthorizationCodeFlow flow = new GoogleAuthorizationCodeFlow.Builder(
						httpTransport, jsonFactory, CLIENT_ID, CLIENT_SECRET, Arrays.asList(DriveScopes.DRIVE))
						.setAccessType("online")
						.setApprovalPrompt("auto").build();

				String url = flow.newAuthorizationUrl().setRedirectUri(REDIRECT_URI).build();
				System.out.println("Please open the following URL in your browser then type the authorization code:");
				System.out.println("  " + url);
				BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
				String code = null;
				try { code = br.readLine(); } catch (IOException ignore) { }

				GoogleTokenResponse response = null;
				try {
					response = flow.newTokenRequest(code).setRedirectUri(REDIRECT_URI).execute();
				} catch (IOException ignore) {
					System.out.println(ignore);
				}
				GoogleCredential credential = new GoogleCredential().setFromTokenResponse(response);

				//Create a new authorized API client
				Drive service = new Drive.Builder(httpTransport, jsonFactory, credential).build();
				try {
					for (File file : service.files().list().execute().getItems()) {
						System.out.println(file.getDownloadUrl());
					}
				} catch (IOException ignore) {}

				//Insert a file
//				File body = new File();
//				body.setTitle("My document");
//				body.setDescription("A test document");
//				body.setMimeType("text/plain");
//
//				java.io.File fileContent = new java.io.File("document.pdf");
//				FileContent mediaContent = new FileContent("application/pdf", fileContent);
//
//				File file = null;
//				try { file = service.files().insert(body, mediaContent).execute(); } catch (IOException ignore) { }
//				System.out.println("File ID: " + file.getId());

			}
		});
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		menu.add("STATS")
				.setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS | MenuItem.SHOW_AS_ACTION_WITH_TEXT);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		Intent statsActivityIntent = new Intent(this, StatsActivity.class);
		startActivity(statsActivityIntent);
		return true;
	}
}
