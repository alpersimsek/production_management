<!--
GDPR Tool Help Page - User Guide and Instructions

This component provides comprehensive help and documentation for users of the GDPR compliance tool.
It includes step-by-step instructions for all major features, troubleshooting tips, and best practices.

Key Features:
- Getting Started Guide: Initial setup and login instructions
- Feature Documentation: Detailed explanations of all app features
- Step-by-Step Tutorials: Guided instructions for common tasks
- Troubleshooting: Common issues and solutions
- Best Practices: Recommendations for effective GDPR compliance
- FAQ Section: Frequently asked questions and answers

Sections:
- Overview: Introduction to the GDPR tool
- Getting Started: Login and initial setup
- Dashboard: Understanding the main dashboard
- File Management: Uploading and processing files
- Search & Masking: Finding and masking sensitive data
- Presets & Rules: Creating and managing data masking rules
- User Management: Admin user management features
- Troubleshooting: Common issues and solutions
- Best Practices: GDPR compliance recommendations

The component provides a comprehensive resource for users to understand
and effectively use all features of the GDPR compliance tool.
-->

<script setup>
import { ref } from 'vue'
import MainLayout from '../components/MainLayout.vue'
import { 
  BookOpenIcon, 
  UserIcon, 
  DocumentIcon, 
  MagnifyingGlassIcon, 
  CogIcon, 
  UsersIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  QuestionMarkCircleIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

// State for collapsible sections
const expandedSections = ref(new Set(['dashboard']))

const toggleSection = (sectionId) => {
  if (expandedSections.value.has(sectionId)) {
    expandedSections.value.delete(sectionId)
  } else {
    expandedSections.value.add(sectionId)
  }
}

const isExpanded = (sectionId) => expandedSections.value.has(sectionId)

// Help sections data
const helpSections = [
  {
    id: 'dashboard',
    title: 'Dashboard Overview',
    icon: CogIcon,
    content: [
      {
        subtitle: 'Understanding the Dashboard',
        steps: [
          'The dashboard provides an overview of your GDPR compliance activities',
          'View recent file processing statistics and results',
          'Access quick actions for common tasks',
          'Monitor system status and recent activities'
        ]
      },
      {
        subtitle: 'Welcome Section & Quick Stats',
        steps: [
          'Personalized greeting with your username',
          'Quick stats showing: Users count, Uploads count, Processed files count',
          'Click on stats to navigate directly to relevant sections',
          'Admin users see total user count, regular users see "1"'
        ]
      },
      {
        subtitle: 'Uploads Section',
        steps: [
          'Shows all files you have uploaded but not yet processed',
          'Click the expand arrow to view detailed file list',
          'For each file you can: Process, Download, or Delete',
          'Processing status shows real-time progress with time estimates',
          'Use pagination to navigate through multiple files'
        ]
      },
      {
        subtitle: 'Processed Files Section',
        steps: [
          'Displays all files that have been successfully processed',
          'Click the expand arrow to view detailed file list',
          'For each processed file you can: Download or Delete',
          'Processed files are ready for use with sensitive data masked',
          'Use pagination to navigate through multiple processed files'
        ]
      },
      {
        subtitle: 'Management Actions Cards',
        steps: [
          'File Management Card: Quick access to full file management interface',
          'User Management Card: Available only to admin users for user administration',
          'Click "Manage Files" or "View All Users" to navigate to detailed sections',
          'These cards provide shortcuts to the main application features'
        ]
      },
      {
        subtitle: 'Navigation',
        steps: [
          'Use the top navigation bar to access different sections',
          'Available sections depend on your user role (admin vs regular user)',
          'Click on any navigation item to switch between pages',
          'The active page is highlighted in the navigation bar'
        ]
      }
    ]
  },
  {
    id: 'presets-rules',
    title: 'Presets & Rules Management',
    icon: CogIcon,
    content: [
      {
        subtitle: 'Understanding the Hierarchy',
        steps: [
          'Products: Top-level categories that organize your data processing',
          'Presets: Templates that define which rules to apply for a specific product',
          'Rules: Individual masking patterns (IP addresses, emails, etc.)',
          'When processing files, you select a product, which applies its preset rules',
          'This hierarchy ensures consistent and organized data masking'
        ]
      },
      {
        subtitle: 'Creating Products',
        steps: [
          'Navigate to Presets section (Admin only)',
          'Click "Add Product" to create a new product',
          'Enter the product name and description',
          'Save the product to make it available for preset assignment',
          'Products help organize presets and apply specific masking rules'
        ]
      },
      {
        subtitle: 'Creating Presets',
        steps: [
          'Click "Add Preset" to create a new preset',
          'Select the product this preset belongs to from the dropdown',
          'Enter a descriptive name for the preset',
          'Configure header matching expressions (optional but recommended)',
          'Header expressions help identify which preset to use based on matched expressions at the first few lines of the file',
          'Save the preset to make it available for file processing'
        ]
      },
      {
        subtitle: 'Managing Custom Rules',
        steps: [
          'Click "Manage Rules" to access the rules management interface',
          'View all available rules with their patterns and configurations',
          'Click "Add Rule" to create a new custom rule',
          'Define rule name and category (IPV4_ADDR, MAC_ADDR, etc.)',
          'Set the pattern or regex for data detection',
          'Choose the masking method (replace, hash, encrypt)',
          'Save and activate the rule for use in presets'
        ]
      },
      {
        subtitle: 'Adding Rules to Presets',
        steps: [
          'Find the preset you want to add rules to',
          'Click "Add Rule" next to the preset',
          'Select an existing rule from the dropdown list',
          'Configure any specific settings for this rule in the preset',
          'Save to add the rule to the preset',
          'The rule will now be applied when this preset is used for processing'
        ]
      },
      {
        subtitle: 'Editing and Deleting',
        steps: [
          'Edit presets by clicking the edit icon next to any preset',
          'Remove rules from presets using the delete icon',
          'Delete entire presets if they are no longer needed',
          'Edit custom rules through the "Manage Rules" interface',
          'All changes are saved immediately and take effect for new processing'
        ]
      },
      {
        subtitle: 'Understanding Modal Windows',
        steps: [
          'Add Product Modal: Create new product categories for organizing presets',
          'Add Preset Modal: Create preset templates with header matching expressions',
          'Manage Rules Modal: View, create, edit, and delete custom masking rules',
          'Add New Rule Modal: Define new masking patterns with regex expressions',
          'Add Rule to Preset Modal: Select existing rules to apply to specific presets',
          'All modals include helpful descriptions and guidance text',
          'Modals are designed to be responsive and work on all screen sizes'
        ]
      }
    ]
  },
  {
    id: 'file-management',
    title: 'File Management',
    icon: DocumentIcon,
    content: [
      {
        subtitle: 'Uploading Files',
        steps: [
          'Navigate to the Files section from the main menu',
          'Click "Upload File" or drag and drop files into the upload area',
          'Supported formats: CSV, Excel, JSON, and text files',
          'Wait for the upload to complete and verify the file appears in your file list'
        ]
      },
      {
        subtitle: 'Processing Files',
        steps: [
          'Select a file from your uploaded files list',
          'Click "Process" to start the masking operation',
          'A new window will popup asking you to select the product that the file belongs to',
          'Choose the appropriate product from the dropdown menu',
          'This will apply the masking rules specific to that product',
          'Click "Confirm" to proceed with processing',
          'If you need to cancel, click "Cancel" to return to the file list',
          'Monitor the progress and wait for processing to complete',
          'Download the processed file when complete'
        ]
      },
      {
        subtitle: 'File Management',
        steps: [
          'View all your uploaded files in the file list',
          'After processing, only processed files are visible (original files are not shown)',
          'Download processed files as needed',
          'Delete files you no longer need',
          'Check processing status and any error messages',
          'Note: Original files are automatically removed after successful processing'
        ]
      }
    ]
  },
  {
    id: 'search-masking',
    title: 'Search & Data Masking',
    icon: MagnifyingGlassIcon,
    content: [
      {
        subtitle: 'Searching for Sensitive Data',
        steps: [
          'Navigate to the Search section',
          'Enter search terms or patterns to find sensitive data',
          'Use advanced search options for more specific queries',
          'Review search results and identify data that needs masking'
        ]
      }
    ]
  },
  {
    id: 'user-management',
    title: 'User Management',
    icon: UsersIcon,
    content: [
      {
        subtitle: 'Managing Users (Admin Only)',
        steps: [
          'Navigate to Users section (Admin only)',
          'View all registered users and their roles',
          'Add new users by clicking "Add User"',
          'Edit user information and roles as needed',
          'Deactivate users who no longer need access'
        ]
      },
      {
        subtitle: 'User Roles',
        steps: [
          'Admin: Full access to all features including user management',
          'User: Access to file processing, search, and dashboard features',
          'Roles determine which features are available in the navigation',
          'Contact your administrator to change your role if needed'
        ]
      }
    ]
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    icon: ExclamationTriangleIcon,
    content: [
      {
        subtitle: 'Common Issues',
        steps: [
          'Login Problems: Verify username/password, check account status',
          'File Upload Issues: Check file format, size limits, and network connection',
          'Processing Errors: Review error messages, check file format compatibility',
          'Permission Errors: Ensure you have the correct role for the operation'
        ]
      },
      {
        subtitle: 'Error Messages',
        steps: [
          'Read error messages carefully for specific guidance',
          'Check the notification area for detailed error information',
          'Try refreshing the page if you encounter unexpected behavior',
          'Contact your administrator for persistent issues'
        ]
      },
      {
        subtitle: 'Performance Issues',
        steps: [
          'Large files may take longer to process - be patient',
          'Check your internet connection for upload/download issues',
          'Close unnecessary browser tabs to free up memory',
          'Try processing smaller batches of data if possible'
        ]
      },
      {
        subtitle: 'Modal Window Issues',
        steps: [
          'If a modal appears behind another window, try refreshing the page',
          'Ensure you have a stable internet connection when working with modals',
          'If modals are not responsive on mobile, try rotating your device',
          'Close any unnecessary browser tabs to free up memory for modal operations',
          'If you experience z-index issues, try clicking outside the modal and reopening it'
        ]
      }
    ]
  },
  {
    id: 'best-practices',
    title: 'Best Practices',
    icon: LightBulbIcon,
    content: [
      {
        subtitle: 'GDPR Compliance',
        steps: [
          'Always review data before processing to ensure appropriate masking',
          'Use strong masking methods for highly sensitive data',
          'Keep audit logs of all data processing activities',
          'Regularly review and update masking rules as needed'
        ]
      },
      {
        subtitle: 'Data Security',
        steps: [
          'Never share processed files containing sensitive data',
          'Use secure channels for file transfer and storage',
          'Regularly review user access and permissions',
          'Implement proper backup and recovery procedures'
        ]
      },
      {
        subtitle: 'Efficiency Tips',
        steps: [
          'Create reusable presets for common data types',
          'Test rules on small samples before processing large files',
          'Organize files with descriptive names for easy identification',
          'Use batch processing for multiple similar files'
        ]
      }
    ]
  },
  {
    id: 'faq',
    title: 'Frequently Asked Questions',
    icon: QuestionMarkCircleIcon,
    content: [
      {
        subtitle: 'General Questions',
        steps: [
          'Q: What file formats are supported? A: CSV, Excel (.xlsx), JSON, and text files',
          'Q: How long does file processing take? A: Depends on file size and complexity, usually seconds to minutes',
          'Q: Can I process multiple files at once? A: Yes, you can upload and process multiple files',
          'Q: Is my data secure? A: Yes, all data is processed securely and not stored permanently',
          'Q: Why do I need to select a product when processing? A: Product selection helps categorize and organize your processed files',
          'Q: Where are my original files after processing? A: Original files are automatically removed after successful processing for security',
          'Q: What are header expressions in presets? A: Header expressions help identify which preset to use based on matched expressions at the first few lines of the file',
          'Q: How does the system choose which preset to use? A: The system looks for header expressions in the first few lines of files and matches them to preset configurations'
        ]
      },
      {
        subtitle: 'Technical Questions',
        steps: [
          'Q: What happens if my session expires? A: You will be redirected to login, your work is saved',
          'Q: Can I customize masking rules? A: Yes, admins can create custom rules and presets',
          'Q: How do I recover a processed file? A: Processed files are available for download in the Files section',
          'Q: What if I encounter an error? A: Check the error message and contact support if needed',
          'Q: Can I open the app in multiple browser tabs? A: Yes, authentication tokens are shared across tabs',
          'Q: How many rules can I display per page? A: The rules management interface shows 3 rules per page for better readability',
          'Q: What if modals appear behind other windows? A: This is usually a browser issue - try refreshing the page or closing unnecessary tabs'
        ]
      }
    ]
  }
]
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">
      <!-- Header Section -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-gradient-to-br from-gray-500 to-slate-600 rounded-2xl flex items-center justify-center shadow-lg">
              <BookOpenIcon class="h-6 w-6 text-white transition-transform duration-300 hover:scale-110" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-slate-900 tracking-tight">GDPR Tool Help Center</h1>
              <p class="mt-1 text-sm text-slate-600 font-medium">Comprehensive guide to using the GDPR compliance tool effectively and securely</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Help Sections -->
      <div class="space-y-6">
        <div 
          v-for="section in helpSections" 
          :key="section.id"
          class="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300 overflow-hidden"
        >
          <!-- Section Header -->
          <button
            @click="toggleSection(section.id)"
            class="w-full px-6 py-4 text-left hover:bg-slate-50/60 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-inset"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <component :is="section.icon" class="h-6 w-6 text-slate-600" />
                <h2 class="text-xl font-semibold text-slate-900">{{ section.title }}</h2>
              </div>
              <component 
                :is="isExpanded(section.id) ? ChevronDownIcon : ChevronRightIcon" 
                class="h-5 w-5 text-slate-400 transition-transform duration-200"
                :class="{ 'rotate-90': isExpanded(section.id) }"
              />
            </div>
          </button>

          <!-- Section Content -->
          <div 
            v-if="isExpanded(section.id)"
            class="px-6 pb-6 border-t border-slate-100"
          >
            <div class="pt-6 space-y-8">
              <div 
                v-for="(item, index) in section.content" 
                :key="index"
                class="space-y-4"
              >
                <h3 class="text-lg font-medium text-slate-800 flex items-center">
                  <div class="w-2 h-2 bg-slate-500 rounded-full mr-3"></div>
                  {{ item.subtitle }}
                </h3>
                
                <!-- Steps List -->
                <div class="ml-5 space-y-3">
                  <div 
                    v-for="(step, stepIndex) in item.steps" 
                    :key="stepIndex"
                    class="flex items-start space-x-3"
                  >
                    <div class="flex-shrink-0 w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center mt-0.5">
                      <span class="text-xs font-medium text-slate-600">{{ stepIndex + 1 }}</span>
                    </div>
                    <p class="text-slate-700 leading-relaxed">{{ step }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Support -->
      <div class="mt-12 bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300">
        <div class="p-6">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-slate-900 mb-2">Need More Help?</h2>
            <p class="text-slate-600">
              If you can't find what you're looking for or need additional assistance, 
              contact our support team directly.
            </p>
          </div>
          <div class="bg-slate-50/60 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-slate-800 mb-4 text-center">Contact Support Team</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="flex items-center space-x-3">
                <UserIcon class="h-5 w-5 text-slate-600 flex-shrink-0" />
                <a href="mailto:asimsek@rbbn.com" class="text-slate-600 hover:text-slate-800 font-medium transition-colors duration-200 text-sm sm:text-base">
                  asimsek@rbbn.com
                </a>
              </div>
              <div class="flex items-center space-x-3">
                <UserIcon class="h-5 w-5 text-slate-600 flex-shrink-0" />
                <a href="mailto:SChandrasekhar@rbbn.com" class="text-slate-600 hover:text-slate-800 font-medium transition-colors duration-200 text-sm sm:text-base">
                  SChandrasekhar@rbbn.com
                </a>
              </div>
              <div class="flex items-center space-x-3">
                <UserIcon class="h-5 w-5 text-slate-600 flex-shrink-0" />
                <a href="mailto:vbenli@rbbn.com" class="text-slate-600 hover:text-slate-800 font-medium transition-colors duration-200 text-sm sm:text-base">
                  vbenli@rbbn.com
                </a>
              </div>
              <div class="flex items-center space-x-3">
                <UserIcon class="h-5 w-5 text-slate-600 flex-shrink-0" />
                <a href="mailto:Dhananjay.Jahagirdar@rbbn.com" class="text-slate-600 hover:text-slate-800 font-medium transition-colors duration-200 text-sm sm:text-base">
                  Dhananjay.Jahagirdar@rbbn.com
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

