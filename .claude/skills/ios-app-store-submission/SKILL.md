---
name: ios-app-store-submission
description: "When the user wants to submit an iOS app to the App Store. Use when the user mentions 'App Store,' 'App Store Connect,' 'TestFlight,' 'iOS submission,' 'app review,' 'EAS build,' 'eas submit,' 'Apple review,' 'app rejection,' or 'iOS release.' This skill covers the entire process from EAS setup to App Store review approval."
---

# iOS App Store Submission

You are an expert in iOS app submission, Apple review guidelines, and EAS (Expo Application Services). Your goal is to guide users through the entire submission process efficiently, avoiding common pitfalls and rejections.

## Core Philosophy

App Store submission is not just about uploading a binary. It's about:
- Meeting Apple's technical and content requirements
- Providing accurate metadata and privacy disclosures
- Preparing for potential review questions
- Streamlining the process for future releases

---

## Quick Reference: Submission Flow

```
1. EAS Setup        → eas init, eas.json, credentials
2. App Store Connect → Create app, fill metadata
3. Privacy Setup    → ATT, Privacy Manifest, data collection
4. Build            → eas build --platform ios --profile production
5. Submit           → eas submit --platform ios
6. Review           → Wait, respond to questions, fix rejections
```

---

## Phase 1: EAS Setup

### 1.1 Prerequisites

```bash
# Install EAS CLI (if not installed)
npm install -g eas-cli

# Login to Expo account
eas login

# Check login status
eas whoami
```

### 1.2 Initialize EAS Project

```bash
cd your-app-directory
eas init
```

This creates/updates:
- `app.json` with `expo.extra.eas.projectId`
- Links project to your Expo account

### 1.3 Configure eas.json

```json
{
  "cli": {
    "version": ">= 16.0.0",
    "appVersionSource": "remote"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": false
      }
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "ios": {
        "autoIncrement": "buildNumber"
      },
      "android": {
        "autoIncrement": "versionCode"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "XXXXXXXXXX"
      }
    }
  }
}
```

**Key fields:**
| Field | Where to find |
|-------|---------------|
| `appleId` | Your Apple ID email |
| `ascAppId` | App Store Connect → App → General → App Information → Apple ID |
| `appleTeamId` | Apple Developer → Membership → Team ID |

### 1.4 Configure app.json for iOS

```json
{
  "expo": {
    "name": "Your App Name",
    "slug": "your-app-slug",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.yourcompany.yourapp",
      "buildNumber": "1",
      "supportsTablet": true,
      "infoPlist": {
        "NSUserTrackingUsageDescription": "This identifier will be used to deliver personalized ads to you.",
        "NSCameraUsageDescription": "Used to take photos for your profile",
        "NSPhotoLibraryUsageDescription": "Used to select photos from your library"
      }
    }
  }
}
```

**Required infoPlist keys by feature:**

| Feature | Key | Example Description |
|---------|-----|---------------------|
| Ads (AdMob) | `NSUserTrackingUsageDescription` | "This identifier will be used to deliver personalized ads to you." |
| Camera | `NSCameraUsageDescription` | "Used to take photos" |
| Photos | `NSPhotoLibraryUsageDescription` | "Used to select photos" |
| Microphone | `NSMicrophoneUsageDescription` | "Used for voice recording" |
| Location | `NSLocationWhenInUseUsageDescription` | "Used to show nearby places" |
| Contacts | `NSContactsUsageDescription` | "Used to find friends" |

---

## Phase 2: App Store Connect Setup

### 2.1 Create App in App Store Connect

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. My Apps → "+" → New App
3. Fill required fields:
   - **Platform**: iOS
   - **Name**: App display name (30 chars max)
   - **Primary Language**: Your main language
   - **Bundle ID**: Must match `bundleIdentifier` in app.json
   - **SKU**: Unique identifier (e.g., `yourapp-ios-001`)

### 2.2 App Information

| Field | Requirements |
|-------|--------------|
| **Name** | 30 chars max, unique on App Store |
| **Subtitle** | 30 chars max, optional but recommended |
| **Category** | Primary + optional secondary |
| **Content Rights** | Does your app contain third-party content? |
| **Age Rating** | Complete questionnaire honestly |

### 2.3 Pricing and Availability

- **Price**: Free or paid tier
- **Availability**: Countries/regions
- **Pre-Orders**: Optional, up to 180 days before release

### 2.4 App Privacy (Critical!)

App Store Connect → App Privacy → Get Started

**Data Types to declare:**

| Category | Examples |
|----------|----------|
| Contact Info | Name, email, phone, address |
| Identifiers | User ID, Device ID, IDFA |
| Usage Data | Product interaction, advertising data |
| Diagnostics | Crash data, performance data |
| Financial | Payment info, credit score |
| Location | Precise/coarse location |

**For each data type, specify:**
1. **Collected?** Yes/No
2. **Linked to identity?** Yes/No
3. **Used for tracking?** Yes/No
4. **Purpose**: App functionality, analytics, advertising, etc.

### 2.5 Version Information

| Field | Requirements |
|-------|--------------|
| **Screenshots** | See screenshot requirements below |
| **Promotional Text** | 170 chars, can update without new version |
| **Description** | 4000 chars max |
| **Keywords** | 100 chars max, comma-separated |
| **Support URL** | Required, must be accessible |
| **Marketing URL** | Optional |
| **What's New** | Required for updates |

---

## Phase 3: Privacy Requirements

### 3.1 App Tracking Transparency (ATT)

Required if you use IDFA for:
- Advertising
- Analytics that links to other companies' data

**Implementation (already in app.json):**
```json
{
  "ios": {
    "infoPlist": {
      "NSUserTrackingUsageDescription": "This identifier will be used to deliver personalized ads to you."
    }
  }
}
```

**In code (if using AdMob):**
```typescript
import { requestTrackingPermissionsAsync } from 'expo-tracking-transparency';

async function requestTracking() {
  const { status } = await requestTrackingPermissionsAsync();
  // status: 'granted' | 'denied' | 'undetermined'
}
```

### 3.2 Privacy Manifest (iOS 17+)

Required for apps using certain APIs. Expo handles most cases automatically, but verify:

**Required Reasons APIs:**
- File timestamp APIs
- System boot time APIs
- Disk space APIs
- Active keyboard APIs
- User defaults APIs

**Check if needed:**
```bash
# After building, check the generated Privacy Manifest
# Located in: ios/YourApp/PrivacyInfo.xcprivacy
```

### 3.3 Third-Party SDK Privacy

If using SDKs like AdMob, Firebase, etc., ensure they include their own privacy manifests. Expo SDK 50+ handles this automatically for most common SDKs.

---

## Phase 4: Screenshots & Assets

### 4.1 Required Screenshots

| Device | Size (pixels) | Required |
|--------|---------------|----------|
| 6.7" iPhone | 1290 x 2796 | Yes (iPhone 15 Pro Max) |
| 6.5" iPhone | 1284 x 2778 | Yes (iPhone 14 Plus) |
| 5.5" iPhone | 1242 x 2208 | Optional |
| 12.9" iPad Pro | 2048 x 2732 | If supports iPad |
| 12.9" iPad Pro (6th gen) | 2048 x 2732 | If supports iPad |

**Tips:**
- 2-10 screenshots per localization
- First screenshot is most important (shown in search)
- Use device frames (optional but professional)
- Show key features, not onboarding screens

### 4.2 App Icon

Already in `app.json`:
```json
{
  "expo": {
    "icon": "./assets/icon.png"
  }
}
```

Requirements:
- 1024 x 1024 pixels
- PNG format
- No transparency
- No rounded corners (iOS adds them)

### 4.3 App Preview (Video)

Optional but effective:
- 15-30 seconds
- Shows app in action
- Device frame optional
- No prices or "free" in video

---

## Phase 5: Build & Submit

### 5.1 Production Build

```bash
# Build for iOS App Store
eas build --platform ios --profile production

# Wait for build (15-30 minutes)
# EAS handles:
# - Certificate management
# - Provisioning profiles
# - Code signing
```

### 5.2 Submit to App Store

**Option A: EAS Submit (Recommended)**
```bash
eas submit --platform ios

# Or specify the build
eas submit --platform ios --latest

# Or with specific build ID
eas submit --platform ios --id BUILD_ID
```

**Option B: Manual (Transporter)**
1. Download `.ipa` from EAS dashboard
2. Open Transporter app (Mac)
3. Upload `.ipa`
4. Select in App Store Connect

### 5.3 TestFlight (Optional but Recommended)

Before App Store submission:
1. Build uploads automatically to TestFlight
2. Add internal testers (up to 100)
3. Add external testers (up to 10,000, requires review)
4. Test thoroughly before submitting for review

---

## Phase 6: App Review

### 6.1 Review Timeline

| Type | Typical Duration |
|------|------------------|
| New App | 24-48 hours |
| Update | 24 hours |
| Expedited Review | 24 hours (request required) |
| Appeal | 3-5 business days |

### 6.2 Common Rejection Reasons & Fixes

#### 1. **Guideline 2.1 - App Completeness**
> "Your app crashed during review"

**Fix:**
- Test on physical devices
- Test with slow network
- Handle all error states
- Check crash logs in Xcode Organizer

#### 2. **Guideline 2.3 - Accurate Metadata**
> "Screenshots don't match app functionality"

**Fix:**
- Update screenshots to match current version
- Don't show features that don't exist
- Ensure descriptions are accurate

#### 3. **Guideline 3.1.1 - In-App Purchase**
> "Unlocking features requires in-app purchase"

**Fix:**
- Digital goods must use IAP
- Physical goods can use external payment
- Services (subscriptions) must use IAP

#### 4. **Guideline 4.2 - Minimum Functionality**
> "App is too simple / just a website wrapper"

**Fix:**
- Add native features
- Ensure app provides value beyond a website
- Use device capabilities

#### 5. **Guideline 5.1.1 - Data Collection**
> "App collects data without disclosure"

**Fix:**
- Update App Privacy in App Store Connect
- Add privacy policy
- Explain data usage in app

#### 6. **Guideline 5.1.2 - Data Use and Sharing**
> "Third-party analytics without consent"

**Fix:**
- Implement ATT for tracking
- Disclose third-party SDKs
- Provide opt-out option

### 6.3 Responding to Rejection

1. **Read carefully**: Understand exactly what's wrong
2. **Don't argue**: Fix the issue, don't debate guidelines
3. **Be specific**: Explain exactly what you changed
4. **Provide demo**: If feature is hidden, explain how to access it
5. **Use Resolution Center**: Respond through App Store Connect

### 6.4 Requesting Expedited Review

When to request:
- Critical bug fix
- Security issue
- Time-sensitive event

How to request:
1. App Store Connect → Your App → App Review
2. Contact Us → Request Expedited Review
3. Explain the urgency clearly

---

## AdMob-Specific Requirements

### Configuration

**app.json:**
```json
{
  "plugins": [
    [
      "react-native-google-mobile-ads",
      {
        "androidAppId": "ca-app-pub-XXXXXXX~YYYYYYY",
        "iosAppId": "ca-app-pub-XXXXXXX~YYYYYYY"
      }
    ]
  ]
}
```

### ATT Implementation

```typescript
import { requestTrackingPermissionsAsync } from 'expo-tracking-transparency';
import mobileAds, { AdsConsent } from 'react-native-google-mobile-ads';

async function initializeAds() {
  // 1. Request ATT permission
  const { status } = await requestTrackingPermissionsAsync();

  // 2. Configure consent (GDPR)
  await AdsConsent.requestInfoUpdate();
  const consentInfo = await AdsConsent.loadAndShowConsentFormIfRequired();

  // 3. Initialize ads
  await mobileAds().initialize();
}
```

### App Privacy Declaration for AdMob

In App Store Connect → App Privacy, declare:

| Data Type | Collected | Linked | Tracking |
|-----------|-----------|--------|----------|
| Device ID | Yes | Yes | Yes (if ATT granted) |
| Product Interaction | Yes | No | No |
| Advertising Data | Yes | Yes | Yes |
| Crash Data | Yes | No | No |

---

## Checklist: Pre-Submission

### Technical
- [ ] `eas.json` configured with correct Apple credentials
- [ ] `app.json` has correct `bundleIdentifier`, `version`, `buildNumber`
- [ ] All `infoPlist` permissions have descriptions
- [ ] No hardcoded test/development values
- [ ] Tested on physical device
- [ ] No crashes or critical bugs

### App Store Connect
- [ ] App created with correct Bundle ID
- [ ] App Information completed
- [ ] Pricing set
- [ ] Age Rating completed
- [ ] App Privacy completed
- [ ] All screenshots uploaded
- [ ] Description and keywords set
- [ ] Support URL accessible
- [ ] Privacy Policy URL set

### Privacy
- [ ] ATT implemented (if using ads)
- [ ] Privacy policy published and linked
- [ ] Data collection accurately declared
- [ ] Third-party SDK disclosures complete

### Final
- [ ] Tested on TestFlight (recommended)
- [ ] Version number makes sense
- [ ] "What's New" written (for updates)
- [ ] Marketing materials ready for launch

---

## Useful Commands Reference

```bash
# EAS Setup
eas login                    # Login to Expo
eas init                     # Initialize project
eas credentials              # Manage certificates

# Building
eas build --platform ios --profile production    # Production build
eas build --platform ios --profile preview       # Internal testing
eas build:list                                   # List builds

# Submitting
eas submit --platform ios                        # Submit latest
eas submit --platform ios --latest               # Submit most recent build
eas submit --platform ios --id BUILD_ID          # Submit specific build

# Debugging
eas build:inspect --platform ios                 # Inspect build config
eas diagnostics                                  # Check EAS setup
```

---

## Related Skills

- **android-play-store-submission**: For Google Play Store submission
- **launch-strategy**: For planning your app launch
- **marketing-psychology**: For App Store optimization (ASO)
- **analytics-tracking**: For setting up analytics properly
